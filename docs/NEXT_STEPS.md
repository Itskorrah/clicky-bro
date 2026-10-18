# clicky-bro: current position and next acceptance work

Updated 18 October 2026. The six authorized workstreams have progressed into a
native development build. They are not all accepted product milestones. See
[BUILD_STATUS.md](BUILD_STATUS.md) for exact checks and remaining limits.

## What has progressed

1. **Foundation comparison:** built/tested both candidates and adopted the pinned
   native OpenClicky source. Decision and licenses are recorded.
2. **Local development:** isolated identity, data and credentials; direct Gemini
   runtime; repeatable build/test/launch commands; Evolve and independent review.
3. **Ask/Teach:** chosen-window macOS capture, visible stop-sharing control,
   streaming Gemini answers and observation-based teaching verification. The
   authoritative native unit suite passed 705/705 with no skips for the
   functional, privacy and Stop-observer changes. The final standalone app build
   passed after the accessibility-row follow-up, but the focused helper-button
   UI test timed out enabling automation before its body ran. Native
   permission/focus/capture and UI acceptance remain outstanding.
4. **Voice/actions:** native system speech passed a real smoke check. Adopted
   dictation remains subject to microphone/focus/insertion tests. Action loops are
   bounded, confirm actions and reject unsuccessful terminal model responses.
5. **Windows:** the final-source core suite ran on this Mac with 1,066 passing
   cases and five failures identical to the untouched upstream baseline. The
   latest WPF cross-build passed after restoring from the existing isolated
   NuGet cache with absolute paths. The user has explicitly deferred Windows
   desktop testing.
6. **Persistent work:** macOS Helpers, explicit Memory, session-enabled Routines
   and saved Runs/text artifacts. The direct Gemini agent supports bounded
   workspace file tools. A live text-only helper run and restart persistence
   passed on 18 October: its exact result and inline artifact remained visible
   after relaunch, and migration preserved the prior completed run. General
   connectors/MCP and Windows workspace UI parity are still open; inherited
   source presence is not end-to-end acceptance.

## Test the useful slice first

The live text-only helper run and restart persistence flow passed; the exact
result, `CLICKY_BRO_HELPER_OK`, and its inline artifact remained visible after
relaunch. The launcher stages the agent in the clicky-bro cache and uses its
private Application Support runtime; existing `.local` settings/workspace are
migrated once and preserved. The canonical Gemini key stays in
`.local/credentials` and is mirrored privately at launch. Next test a single
disposable workspace file with write permission explicitly enabled.

For native window questions, grant Screen Recording in macOS settings when ready,
share a disposable window, ask a question and stop sharing. Verify capture never
switches to another window or display after the shared window closes. Teach must
wait for the user and verify the result; Agent mode needs a distinct action
confirmation. Test Stop while a model/tool request is pending. At the final
launcher check, Accessibility, Screen Recording and microphone diagnostics were
false and `screenContent` was false; permission/capture acceptance still needs
the explicit current-bundle check in [TESTING_MACOS.md](TESTING_MACOS.md).

Then test dictation into a disposable editor, changing focus during capture and
before insertion. Confirm voice cancellation, permission denial and error recovery.
These native observations cannot be inferred from provider or state-machine tests.

## Next engineering slices

- Close native macOS capture, focus, hotkey, dictation and teaching acceptance;
  repair any observed failures before expanding autonomous capabilities.
- Bring the Helpers/Memory/Routines UI and persistence contracts to Windows;
  then use [TESTING_WINDOWS.md](TESTING_WINDOWS.md) on the user's PC when ready.
- Add one useful connector through the Gemini runtime with scoped authentication,
  denial/revocation tests and real action receipts. General MCP and multi-account
  integrations remain separate work, not automatically supported by adoption.
- Extend artifacts beyond saved text with safe previews and correct provenance.
  Add helper follow-up/steering and explicitly designed restart/resume semantics.
- Close the feature crosswalk one verified workflow at a time. Suggestions,
  accounts/plans/teams/referrals, signed installers and trusted updates follow
  working core workflows and remain unimplemented commercial work.

Use GPT-6.1 Sol High for the root task and GPT-6 Luna Max for the delegated
Windows lane, as verified from task metadata. These assignments did not change
host/global settings. Keep the main orchestration short, at no more than two
workers, and serialize expensive builds on this Mac. Use an independent reviewer
for native authority/persistence changes and keep bounded free-provider checks
separate from offline verification.
