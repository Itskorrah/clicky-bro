#!/usr/bin/env python3
"""clicky-bro's local Gemini setup and bounded connection checks (Python 3.9+).

No SDK, automatic retries, paid tools, or provider fallback. Credentials never
appear in URLs, command-line arguments, evidence, or printed provider errors.
"""

import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zlib

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / '.local/credentials/gemini.json'
MODELS = ('gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-3.8-flash')
API = 'https://generativelanguage.googleapis.com/v1beta/models/'


class SetupError(Exception):
    """An error whose message is safe to display."""


def save_key(key, path=KEY_FILE):
    key = key.strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{30,200}', key):
        raise SetupError('Key format is invalid; existing credential was preserved.')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink() or path.is_symlink():
        raise SetupError('Refusing a symlink credential location.')
    if os.name == 'posix':
        path.parent.chmod(0o700)
    fd, tmp = tempfile.mkstemp(prefix='.gemini-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump({'api_key': key}, out)
            out.write('\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_key(path=KEY_FILE):
    try:
        if path.is_symlink() or path.parent.is_symlink():
            raise SetupError('Refusing a symlink credential location.')
        if os.name == 'posix' and stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise SetupError('Credential permissions must be private (chmod 600).')
        key = json.loads(path.read_text())['api_key']
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{30,200}', key):
            raise ValueError()
        return key
    except FileNotFoundError:
        raise SetupError('No local key. Run: python3 scripts/gemini.py configure') from None
    except (ValueError, KeyError, TypeError):
        raise SetupError('Invalid credential file; run configure to replace it.') from None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SetupError('Redirect refused; credentials were not forwarded.')


class Gemini:
    def __init__(self, key, model=MODELS[0], opener=None):
        if model not in MODELS:
            raise SetupError('Model is outside the development allowlist.')
        self._key = key
        self.model = model
        self.requests = 0
        self.opener = opener or urllib.request.build_opener(NoRedirect())

    def generate(self, contents, functions=None, tool_mode='AUTO', json_output=False):
        body = {
            'contents': contents,
            'generationConfig': {'maxOutputTokens': 1024, 'temperature': 0},
        }
        if functions:
            body['tools'] = [{'functionDeclarations': functions}]
            body['toolConfig'] = {'functionCallingConfig': {'mode': tool_mode}}
        if json_output:
            body['generationConfig']['responseMimeType'] = 'application/json'
        req = urllib.request.Request(
            API + self.model + ':generateContent',
            data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json', 'x-goog-api-key': self._key},
            method='POST',
        )
        self.requests += 1
        try:
            with self.opener.open(req, timeout=45) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            # Never print a raw upstream message: it may contain credentials/data.
            try:
                raw = error.read(32768).decode('utf-8', errors='replace')
            finally:
                error.close()
            if 'leaked' in raw.lower():
                reason = 'Google reports this key as leaked; replace it with configure.'
            else:
                reason = {
                    400: 'Request or API key rejected; inspect local setup.',
                    401: 'Authentication failed; replace the key with configure.',
                    403: 'Key permission denied or API access unavailable.',
                    404: 'Model or endpoint unavailable. No fallback attempted.',
                    429: 'Quota or capacity exhausted. No automatic retry attempted.',
                }.get(error.code, 'Provider request failed; no automatic retry attempted.')
            raise SetupError('HTTP %s: %s' % (error.code, reason)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise SetupError('Network/TLS request failed; no automatic retry attempted.') from None
        except (ValueError, TypeError):
            raise SetupError('Provider response was not valid JSON.') from None
        if not isinstance(data, dict):
            raise SetupError('Unexpected provider response type.')
        return data


def user(parts):
    return {'role': 'user', 'parts': parts}


def content(response):
    try:
        result = response['candidates'][0]['content']
        if not isinstance(result['parts'], list):
            raise ValueError()
        return result
    except (KeyError, IndexError, TypeError, ValueError):
        raise SetupError('Provider returned no usable candidate.') from None


def text_of(response):
    return ''.join(p.get('text', '') for p in content(response)['parts'] if not p.get('thought')).strip()


def image_fixture():
    """240x120 RGB PNG: red left half, blue right half. No user screen data."""
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    row = b'\x00' + bytes((255, 0, 0)) * 120 + bytes((0, 0, 255)) * 120
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('!IIBBBBB', 240, 120, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(row * 120)) + chunk(b'IEND', b''))


def probe(client):
    report = {'model': client.model, 'checks': {}, 'scope': 'synthetic API checks; no desktop control'}
    checks = report['checks']
    try:
        response = client.generate([user([{'text': 'Reply with exactly CLICKY_BRO_OK and nothing else.'}])])
        checks['text'] = text_of(response) == 'CLICKY_BRO_OK'
        if not checks['text']:
            raise SetupError('Text check returned an unexpected answer.')

        # Stay below the configured minimum RPM allowance; never retry a failure.
        time.sleep(2)
        response = client.generate([user([
            {'text': 'Inspect this image. Return JSON with keys left and right, each the lowercase English name of the color on that half. No other keys.'},
            {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(image_fixture()).decode()}},
        ])], json_output=True)
        try:
            colors = json.loads(text_of(response))
        except ValueError:
            colors = None
        checks['image_input'] = colors == {'left': 'red', 'right': 'blue'}
        if not checks['image_input']:
            raise SetupError('Synthetic image check returned an unexpected answer.')

        time.sleep(2)
        functions = [{'name': 'add_integers', 'description': 'Add two integers using a local test calculator.',
                      'parameters': {'type': 'OBJECT', 'properties': {'a': {'type': 'INTEGER'}, 'b': {'type': 'INTEGER'}},
                                     'required': ['a', 'b']}}]
        initial = user([{'text': 'Use the add_integers tool to calculate 7 plus 5.'}])
        response = client.generate([initial], functions=functions, tool_mode='ANY')
        model_content = content(response)
        calls = [part['functionCall'] for part in model_content['parts'] if 'functionCall' in part]
        checks['tool_call'] = (len(calls) == 1 and calls[0].get('name') == 'add_integers'
                               and calls[0].get('args') == {'a': 7, 'b': 5})
        if not checks['tool_call']:
            raise SetupError('Model did not request the expected calculator function.')
        # This is the only tool we execute. Model output never becomes shell code.
        result = calls[0]['args']['a'] + calls[0]['args']['b']
        time.sleep(2)
        response = client.generate([
            initial, model_content,
            user([{'functionResponse': {'name': 'add_integers', 'response': {'result': result}}},
                  {'text': 'Reply with only the numeric result.'}]),
        ], functions=functions, tool_mode='NONE')
        checks['tool_round_trip'] = text_of(response).strip() == '12'
        if not checks['tool_round_trip']:
            raise SetupError('Tool result round trip returned an unexpected answer.')
        report['passed'] = True
    except SetupError as error:
        report.update(passed=False, error=str(error))
    report['requests_attempted'] = client.requests
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('configure', 'status', 'test'))
    parser.add_argument('--model', choices=MODELS, default=MODELS[0])
    args = parser.parse_args()
    if args.command == 'configure':
        if not sys.stdin.isatty():
            raise SetupError('Run configure in an interactive terminal; input is hidden.')
        save_key(getpass.getpass('Paste replacement Gemini key (hidden): '))
        print('Local key saved. Existing model configuration is unchanged.')
    elif args.command == 'status':
        load_key()
        print('Local credential is present and private. Validity requires a live test.')
        print('Default model:', MODELS[0])
    else:
        report = probe(Gemini(load_key(), args.model))
        path = ROOT / '.local/evidence/gemini-connection.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        report['checked_at_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        path.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (SetupError, OSError) as error:
        print(str(error) if isinstance(error, SetupError) else 'Local file operation failed.', file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled; no request retried.', file=sys.stderr)
        sys.exit(130)
