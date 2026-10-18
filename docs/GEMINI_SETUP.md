# clicky-bro: local Gemini development connection

The repository contains the adopted native desktop source, a direct Gemini
runtime and local development commands. See [BUILD_STATUS.md](BUILD_STATUS.md)
for current evidence and platform limits, and the root README to build/run it.

## Commands

Run from `/Users/korrah/Documents/ChatGPT/clicky-pal`:

```bash
python3 scripts/gemini.py status
python3 scripts/gemini.py test
```

The default development candidate is `gemini-3.5-flash-lite`. Explicit comparison:

```bash
python3 scripts/gemini.py test --model gemini-3.8-flash
```

Each successful test run makes four requests: exact text response, generated
image recognition, calculator function selection, and tool-result continuation.
It never captures the desktop, sends user documents, or executes computer-control
tools. A failure stops the run; there is no automatic retry or model fallback.
Evidence is written to `.local/evidence/gemini-connection.json`; each run replaces
the previous report. Evidence contains check results and request counts, never
the key, raw provider errors, or private conversation content.

## Replace the temporary key later

1. Create a replacement Gemini key in the same Google AI Studio project.
2. In a normal Terminal window, run:

   ```bash
   cd /Users/korrah/Documents/ChatGPT/clicky-pal
   python3 scripts/gemini.py configure
   ```

3. Paste the replacement at the hidden prompt and press Return. It is normal
   that no characters appear. The existing credential is replaced atomically.
4. Quit and relaunch clicky-bro so the native app reloads the key; an already
   running process keeps the previous key in memory. Then run
   `python3 scripts/gemini.py test`. Once it passes, revoke the old key.

The canonical local credential is in `.local/credentials/gemini.json`. On this
Mac the directory is owner-only (0700) and the file is owner-read/write (0600).
The developer launcher validates it and refreshes a private copy at
`~/Library/Application Support/clicky-bro/development/credentials/gemini.json`
for the native app. Replacing the canonical key does not update an already
running app; quit and relaunch with `python3 scripts/dev.py launch` so it reads
the refreshed copy. This is a private local file, not encrypted Keychain
storage. Both `.gitignore` and the existing local Git exclusion cover `.local/`.
Do not stage it forcibly or include it in exports. The eventual desktop product
should use the OS credential store. The helper does not change global shell
settings or reuse Codex's credentials. The app launcher's local diagnostic log
is `~/Library/Caches/clicky-bro/development.log`.

## Quotas and limits

The supplied AI Studio screenshots show this project on the Free tier, with
`Gemini 3.5 Flash Lite` and `Gemini 3.1 Flash Lite` each displaying 15 RPM,
250,000 TPM and 500 RPD. `Gemini 3.8 Flash` displays 5 RPM, 250,000 TPM and
20 RPD. These are observed configured limits, not proven independent pools or
guaranteed service capacity. No billing was enabled by this setup.

The CLI restricts requests to those three reviewed model identifiers, limits
output to 1,024 tokens per request, blocks redirects to other endpoints and
does not activate hosted search, code execution or other paid services.
An allowlist is not a billing cap: if project billing, model pricing or quotas
change, review the setup before further calls. An exhausted quota is reported
without automatically switching to a paid model.

## Verification boundaries

Offline verification:

```bash
python3 -m unittest discover -s tests -v
```

Tests cover private credential storage/replacement, rejecting insecure files,
redirect rejection, model allowlisting, safe quota errors without retries,
preserving tool-call metadata and refusing unexpected tools. Fake responses are
explicitly separate from live inference. Live probe results are documented in
`GEMINI_VERIFICATION.md` and the ignored JSON evidence file.

Passing API probes does not prove desktop automation, sustained model quality,
voice input/output, native permission handling or Windows behavior.

## Primary references

- [Gemini 3.5 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
- [GenerateContent API](https://ai.google.dev/api/generate-content)
- [API key management](https://ai.google.dev/gemini-api/docs/api-key)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
