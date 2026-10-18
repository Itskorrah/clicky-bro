# Test clicky-bro on macOS

The macOS app is a local development build. Native Screen Recording permission
and the full selected-window capture flow are **not currently accepted**. A
visible Allowed toggle can belong to an older app build: an ad-hoc rebuild
changed the current app's CDHash, so the existing TCC entry does not establish
permission for this bundle.

## Register the current development build

After the final build:

1. Quit the clicky-bro copy that is running.
2. Open **System Settings > Privacy & Security > Screen & System Audio
   Recording**. Do **not** remove or modify HeyClicky or another product's entry.
   An old Allowed entry does not prove access for the currently running app.
   If the current build is not listed, add the exact bundle in step 3.
3. In Finder, choose **Go > Go to Folder**, enter
   `~/Library/Caches/clicky-bro/DerivedData-local/Build/Products/Debug/OpenClicky.app`,
   and locate that exact app bundle. Add that bundle to Screen & System Audio
   Recording and enable its entry.
4. Relaunch the same app with `python3 scripts/dev.py launch`.

An old OpenClicky entry was observed in the previous developer environment, but
the exact currently running bundle has not been confirmed as allowed. The current bundle has not passed permission
acceptance or a full capture test. Do not count the Settings toggle by itself as
success. A later rebuild can change the app's code identity again and may
require repeating registration until a properly signed distribution provides a
stable identity. No TCC reset or signing configuration change was made.

## Verify capture

On this branch, first open **Settings → Privacy & Security → Selected-window capture test**. With no chosen window, press **Test frame** and confirm it says *No window selected* without opening a picker or sending an image. Then share a disposable window through the companion and press **Test frame** again. Record both independent fields: (a) Screen Recording permission as reported by CoreGraphics, and (b) a successfully delivered **local frame** with dimensions. Do not equate a green system permission row with a successful frame. A passed frame test still does not prove it contains the intended visible content.

Check the following cases separately in the **same build and signature**: denied permission; allowed permission after app restart; selected window moved without resizing while capture is in progress; resized window; window closed; window moved to a second display; Stop during capture; Stop during model/approval; and an app relaunch with no sharing selected. A moved/resized-in-flight window should yield a retriable error, never a stale coordinate mapping or a full-screen image. When sharing stops, any cached realtime image must be cleared.

To identify this *specific* build without changing permissions, run on the Mac (after building):

```sh
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$HOME/Library/Caches/clicky-bro/DerivedData-local/Build/Products/Debug/OpenClicky.app/Contents/Info.plist"
codesign -dv --verbose=4 "$HOME/Library/Caches/clicky-bro/DerivedData-local/Build/Products/Debug/OpenClicky.app" 2>&1
```

Record the macOS version and commit as well. Do not run `tccutil reset`, alter unrelated TCC entries or loosen OS security for testing. If the OS cannot associate permission with ad-hoc builds consistently, stabilise the signing identity and rebuild before retesting.

Use a disposable window with no personal information. Confirm the app captures
only the explicitly selected window, reports a clear failure when access is
denied or that window is unavailable, and never falls back to another window or
the full display. Stop sharing while a request is pending and confirm the app
does not continue using the old image. Record the app build and observed result;
do not include private window contents in screenshots or logs.

Passing source tests or seeing an Allowed toggle does not prove operating-system
capture acceptance. Final launcher diagnostics reported Accessibility, Screen
Recording and microphone unavailable, with `screenContent` false. The current
bundle has not passed permission or full capture acceptance. The authoritative
native unit suite reported 705 passed, 0 failed and 0 skipped for the preceding
functional/privacy/Stop fixes. A later focused helper-button UI test compiled,
but its runner timed out enabling automation mode before its body ran. The final
standalone app build passed. See [BUILD_STATUS.md](BUILD_STATUS.md) and the
[root README](../README.md) for the exact boundaries.

## Verify a persistent helper run

Use the launcher script so the app keeps the private runtime and key paths:
If this is a fresh clone, create the harmless test helper first with instruction
`Reply with exactly CLICKY_BRO_HELPER_OK. Do not use tools.` Set its scope to
text-only and leave memory and file writes off. Otherwise, select that helper.

1. Run `python3 scripts/dev.py launch` from the repository root.
2. In **Helpers**, run **Connection check** and confirm it succeeds.
3. Click **Run now** for the test helper.
4. In **Runs & files**, confirm the completed result is exactly
   `CLICKY_BRO_HELPER_OK`.
5. Quit the app, relaunch with `python3 scripts/dev.py launch`, and confirm the
   saved completed result is still present.

This helper workflow passed live on 18 October 2026. One run completed in 2.313
seconds with exactly `CLICKY_BRO_HELPER_OK` and an inline `Answer.txt` artifact.
After Cmd-Q and relaunch, the same completed result and artifact were visible;
root independently matched them against persisted state. The run ID was
`86714F6C-F141-45B4-AB3A-DE7A55A30A7C`, and the one-time migration preserved an
older completed run as well. Two live Gemini GUI requests were used for this
batch. This accepts the helper/runtime persistence flow only; Screen Recording,
Accessibility, microphone and full capture acceptance remain pending.

The first `python3 scripts/dev.py launch` stages the agent under
`~/Library/Caches/clicky-bro/development` and uses
`~/Library/Application Support/clicky-bro/development` for private settings and
workspace data. Existing `.local/runtime/native` and
`.local/workspaces/default` state is copied once; the original checkout data is
preserved. The canonical key stays in `.local/credentials/gemini.json`, while
the launcher refreshes a private runtime mirror. Replacing the key does not
change an already-running app; quit and relaunch it.

The final standalone app build passed after the accessibility-row source
follow-up. The authoritative native unit suite remains 705 passed, 0 failed,
0 skipped for the preceding functional/privacy/Stop changes. The focused helper
button UI test compiled, but the runner timed out enabling automation mode
before the test body ran; this is not a passing UI result.
