"""Offline tests. These do not contact a model or prove live capabilities."""
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location('gemini', Path(__file__).resolve().parents[1] / 'scripts/gemini.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
TEST_KEY = 'test-placeholder-' + 'x' * 40


class Response(io.BytesIO):
    def __init__(self, data):
        super().__init__(json.dumps(data).encode())


class Opener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return Response(result)


def answer(parts):
    return {'candidates': [{'content': {'role': 'model', 'parts': parts}}]}


class CredentialTests(unittest.TestCase):
    def test_private_atomic_replacement_and_invalid_key_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'credentials/gemini.json'
            g.save_key(TEST_KEY, path)
            self.assertEqual(g.load_key(path), TEST_KEY)
            if os.name == 'posix':
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            with self.assertRaises(g.SetupError):
                g.save_key('bad key', path)
            self.assertEqual(g.load_key(path), TEST_KEY)
            replacement = TEST_KEY + '-new'
            g.save_key(replacement, path)
            self.assertEqual(g.load_key(path), replacement)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permissions')
    def test_insecure_file_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'credentials/gemini.json'
            g.save_key(TEST_KEY, path)
            path.chmod(0o644)
            with self.assertRaises(g.SetupError):
                g.load_key(path)
            link = Path(tmp) / 'linked.json'
            link.symlink_to(path)
            with self.assertRaises(g.SetupError):
                g.save_key(TEST_KEY, link)


class ProviderTests(unittest.TestCase):
    def test_no_redirect_can_forward_credential(self):
        with self.assertRaises(g.SetupError):
            g.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.com')

    def test_unlisted_model_rejected_before_network(self):
        with self.assertRaises(g.SetupError):
            g.Gemini(TEST_KEY, model='unreviewed-paid-model')

    def test_429_is_not_retried_and_raw_error_never_exposed(self):
        error = urllib.error.HTTPError(g.API, 429, 'bad', {}, io.BytesIO(TEST_KEY.encode()))
        opener = Opener([error])
        client = g.Gemini(TEST_KEY, opener=opener)
        with self.assertRaises(g.SetupError) as raised:
            client.generate([g.user([{'text': 'test'}])])
        self.assertNotIn(TEST_KEY, str(raised.exception))
        self.assertIn('429', str(raised.exception))
        self.assertEqual(client.requests, 1)
        self.assertEqual(len(opener.requests), 1)
        request = opener.requests[0]
        self.assertNotIn(TEST_KEY, request.full_url)
        self.assertNotIn(TEST_KEY, request.data.decode())
        self.assertEqual(request.get_header('X-goog-api-key'), TEST_KEY)

    def test_complete_probe_preserves_tool_signature_and_reports_no_secrets(self):
        model_part = {'functionCall': {'name': 'add_integers', 'args': {'a': 7, 'b': 5}},
                      'thoughtSignature': 'synthetic-signature'}
        opener = Opener([
            answer([{'text': 'CLICKY_BRO_OK'}]),
            answer([{'text': '{"left":"red","right":"blue"}'}]),
            answer([model_part]), answer([{'text': '12'}]),
        ])
        with patch.object(g.time, 'sleep'):
            report = g.probe(g.Gemini(TEST_KEY, opener=opener))
        self.assertTrue(report['passed'])
        self.assertEqual(report['requests_attempted'], 4)
        self.assertNotIn(TEST_KEY, json.dumps(report))
        sent = json.loads(opener.requests[-1].data)
        self.assertEqual(sent['contents'][1]['parts'][0], model_part)
        self.assertEqual(sent['toolConfig']['functionCallingConfig']['mode'], 'NONE')

    def test_unexpected_tool_never_executes_and_probe_stops(self):
        opener = Opener([
            answer([{'text': 'CLICKY_BRO_OK'}]),
            answer([{'text': '{"left":"red","right":"blue"}'}]),
            answer([{'functionCall': {'name': 'run_shell', 'args': {'command': 'unsafe'}}}]),
        ])
        with patch.object(g.time, 'sleep'):
            report = g.probe(g.Gemini(TEST_KEY, opener=opener))
        self.assertFalse(report['passed'])
        self.assertEqual(report['requests_attempted'], 3)


if __name__ == '__main__':
    unittest.main()
