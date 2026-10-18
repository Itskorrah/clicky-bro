# clicky-bro: Gemini connection verification

Initial connection verified locally on 17 October 2026, completed at 12:28:19 UTC.
This is the historical provider probe; subsequent native and agent evidence is
recorded in [BUILD_STATUS.md](BUILD_STATUS.md).

## Live provider result

Provider: Google Gemini Developer API. Model: `gemini-3.5-flash-lite`.
Authentication: the temporary Gemini key explicitly authorized by the user,
read from their previously supplied screenshot without printing its contents.
The key was accepted by the API. No Google billing settings were changed.

| Check | Evidence | Result |
| --- | --- | --- |
| Text | Model returned the exact required `CLICKY_BRO_OK` marker | Passed |
| Image input | Generated two-colour PNG supplied without describing its colours; model returned correct left/right colour labels | Passed |
| Function call | Model requested exactly `add_integers` with arguments `a=7`, `b=5` | Passed |
| Tool continuation | Local test calculator returned 12; model consumed that result and returned `12` | Passed |

Four inference requests were attempted; all four completed. No retries, other
models or paid server tools were used. No private desktop screenshots or user
documents were sent. The image was a generated fixture. The API key travelled
only in the authentication header to Google's fixed HTTPS endpoint.

Machine-readable report: `.local/evidence/gemini-connection.json` (ignored by
Git). It contains check outcomes and request count, not credentials or raw
provider messages. A future probe replaces that report.

## Local verification

- `python3 -m unittest discover -s tests -v`: 7 offline tests passed.
- Credential file mode 0600; credential directory mode 0700 on this Mac.
- `git check-ignore` confirms the credential and report paths are excluded.
- Exact credential scan across all non-ignored source files found no copies.
- No additional dependency installation or global configuration changes.

## Limits of the result

This establishes a working local development connection and basic multimodal
and function-calling compatibility. It does not establish reliable autonomous
desktop use, sustained task success, full voice support, Windows acceptance,
independent daily quota pools, or commercial readiness. At the time of this
initial probe the desktop foundation had not been adopted. No comparison run
against Flash or other providers was needed to establish this connection.

The temporary key can be revoked and replaced using the hidden input command
in [GEMINI_SETUP.md](GEMINI_SETUP.md). Keep the replacement out of chat and source.
