# Full competitor specification: coverage and additions

17 October 2026. The supplied specification is independent competitor research written without this project's full context. It is an input to our decisions, not a replacement for the project brief, verified findings, current development protocol or the user's instructions.

> **19 October follow-up:** The native OpenClicky adoption decision is complete;
> see [FOUNDATION_DECISION.md](FOUNDATION_DECISION.md). This remains a requirements
> crosswalk, not an implementation or platform-acceptance report. Current status
> is in [NEXT_STEPS.md](NEXT_STEPS.md) and [BUILD_STATUS.md](BUILD_STATUS.md).

## Review boundary

Read the entire `HeyClicky_Competitive_Research_and_Build_Spec.md`: 48,905 bytes, 403 newline characters / 404 split lines, all 13 numbered sections, 60 catalogue entries, 22 test scenarios, proposed architecture/data objects, security requirements, use cases, deprecated features, delivery order, agent-assignment text and source register. SHA-256: `fde6f47f0dc385c7e459da024d9fcbf2984dbf367e555c83d79ffb49fd977228`.

It is more detailed than the previously pasted summary. Most categories were already represented in our 27-area inventory; this file supplies finer behaviors and explicit acceptance cases. No capability was implemented or test executed as a result of this review. The document's section 11 operating instructions did not authorize implementation, installations, new agents, PRs or a replacement project structure.

Use `HC-A01` through `HC-J06` for imported catalogue entries and `HC-T01` through `HC-T22` for imported tests. Our existing `F01–F27` are broader feature areas; our `A01–A20` are acceptance scenarios. Namespacing prevents collisions, especially imported F01 (integrations) versus existing F01 (voice), and imported A01 versus existing acceptance A01.

The supplied CURRENT labels remain author-attributed shipping claims, not our runtime verification. B08 is historical/paused, E08 is demonstrated, and F06 mixes historical demonstrations with a current label. Keep those qualifications. Community reports and Instagram/video coverage retain the verification limits already recorded.

## Material additions and refinements

1. **Whole-document proof:** HC-T04 asks about page 25 of a 30-page PDF while page 2 is visible. Our document pipeline was planned, but this gives it a concrete acceptance case requiring page/source provenance.
2. **Real connector authentication:** HC-T13 requires validating an MCP token against the actual selected server and distinguishing invalid/re-auth states. A saved token or mocked response cannot count as connected.
3. **Concurrent isolation:** HC-T10 strengthens the existing independent-helper checks into concurrent runs: stop one without affecting the other's work, grants or artifacts.
4. **Quota recovery:** HC-T17 makes budget exhaustion a first-class lifecycle test, including usable UI and retained files/state. Legitimate continuation must still respect the provider/account budget.
5. **Untrusted-input execution test:** HC-T22 requires a hostile email/PDF to fail to induce secret disclosure. This exercises the authority boundary, not merely a prompt saying to ignore attacks.
6. **Precise scheduling:** HC-I03/HC-T14 add a three-actual-failure pause, while sleep/offline/busy waits are separate states rather than actual run failures. One catch-up and bounded retries remain consistent with our plan.
7. **Dictation dictionary learning:** HC-D03 adds a short correction-learning window. If adopted, monitor only the specific recent insertion/field under an explicit preference, with edit/forget/undo controls. This is not permission for global key/clipboard monitoring.
8. **UI completion criteria:** recent-file piles/drag-out, per-chat draft and attachment retention, read/unread state, incremental history and live artifact previews need their own checks within the broader Home/files requirements.
9. **Context minimization:** Home text messages must not automatically attach a screenshot of Home; context should reflect the selected task source. Previous-page context needs a bounded lifetime/source identity.
10. **Privacy evidence:** HC-T20 needs stronger evidence than network logs alone. Network silence cannot prove that a local screenshot was not captured. Use capture-path instrumentation and synthetic local-state checks alongside outbound-request logs, with an explicit observation period and scope.

## Capability crosswalk: all 60 entries

“Covered” means covered by the existing planned feature area, not implemented. “Refine” adds precision to that plan. Milestones refer to BUILD_PLAN.md; the candidate-adoption gate in RESEARCH_UPDATE.md precedes fresh scaffolding.

| Imported ID | Topic | Existing planned area | Disposition / detail to retain |
| --- | --- | --- | --- |
| HC-A01 | Companion and cursor proximity | F19, F20, F26 | Covered; original compact surface, hotkey and multi-monitor behavior; platform-specific appearance. |
| HC-A02 | Notch quick-peek | F19, F16, F10 | Refine; latest-file pile, drag-out and unread state. A macOS surface, with coherent Windows equivalent. |
| HC-A03 | Home workspace | F19, F10, F16 | Refine; per-chat drafts/attachments, incremental history, read/unread and persistent geometry. |
| HC-A04 | Agent status cards | F12, F16, F22 | Covered; current-run outputs, follow-up target identity and quiet announcements. |
| HC-A05 | Character customization | F20, F09, F10 | Covered; original assets and consistent agent identity across surfaces. |
| HC-A06 | Onboarding/tutorial | F21, F09, F24 | Refine; real interaction, replay/skip, permission recovery and separate setup usage. Four questions/three suggestions are competitor flow details, not a required script. |
| HC-A07 | Settings/help | F02, F20, F22, F23, F25 | Covered; settings discoverability and safe settings actions remain scoped. |
| HC-B01 | Triggered screen snapshot | F03, F21 | Covered; explicit capture source/indicator, no undisclosed passive collection. |
| HC-B02 | Beyond-visible document context | F03, F16 | Refine with HC-T04; extract full accessible content with citations/chunking. |
| HC-B03 | Screen-specific Q&A | F03, F04, F08 | Covered; explicit active/previous context identity and freshness. |
| HC-B04 | Pointer guidance | F04 | Covered; visual indication is separate from input; legacy POINT tags are a reference implementation. |
| HC-B05 | Freehand selection | F05 | Covered; annotations are context, not edits in the target application. |
| HC-B06 | Drawings and walkthroughs | F04, F12 | Refine; step verification, pause/recovery and annotation expiry. Fifteen steps is a documented competitor budget, not our architecture's fixed maximum. |
| HC-B07 | Target accuracy/scaling | F03, F04, F13, F26 | Covered; strengthen duplicate-label/icon/moving-window cases and coordinate provenance. |
| HC-B08 | App instructional skills | F15; optional product skills | Historical/paused competitor feature; explicit optional enhancement with versioning and declared capabilities. |
| HC-C01 | Push-to-talk | F01, F02 | Covered; first-word capture, waveform and correct destination. |
| HC-C02 | Text mode | F06, F03 | Refine; hotkey text versus Home text have deliberate context-sharing rules. |
| HC-C03 | Realtime conversation | F01, F02 | Covered; barge-in and recoverable turns. Always-on remains separately gated/experimental. |
| HC-C04 | Voices/devices/quiet behavior | F02, F22 | Covered; previews, pace, device changes and non-intrusive fallback. |
| HC-C05 | Multilingual speech | F01, F07 | Refine; per-provider capabilities and tested language list, not inherited 70+/50+ claims. |
| HC-C06 | Intent routing | F04, F09, F12, F17 | Covered; never mistake a question, a wait instruction or an ambiguous assent for task authority. |
| HC-C07 | Contextual follow-ups | F09, F10, F12 | Covered; stable run/conversation/agent identities across voice sessions. |
| HC-D01 | Fast cross-app dictation | F07, F02 | Covered; benchmark onset and support an explicit app matrix. The 450 ms figure is an advertising claim. |
| HC-D02 | Transcript cleanup | F07 | Covered; preserve meaning/raw transcript and language settings. |
| HC-D03 | Dictionary/correction learning | F07 | Refine; bounded recent-field learning, opt-in, user editing and retention controls. |
| HC-D04 | Selection-aware drafting | F08, F07, F15 | Covered; contextual draft/rewrite and insertion, with separate send authority. |
| HC-D05 | Robust insertion | F07, F12 | Covered; clipboard ownership, focus, terminals, IME/layouts and long-dictation recovery. |
| HC-E01 | Autonomous tasks | F09, F12, F16 | Covered; our installed-app evidence supports embedded Codex packaging/configuration; effective runtime behavior remains partially unverified. |
| HC-E02 | Native computer use | F13 | Covered; target-scoped permission and observed action effects. No universal focus-safe automation claim. |
| HC-E03 | Browser computer use | F14, F13 | Covered; explicit existing-window choice versus one separate task window, with honest fallbacks. |
| HC-E04 | Delegation/isolation | F09, F12 | Strengthen with HC-T10; concurrent work, independent queues, grants and files. |
| HC-E05 | Approval | F13, F15, F12 | Covered; scoped grant lineage/expiry; continuation cannot widen authority or survive revocation. |
| HC-E06 | Progress/stop/retry | F12, F24 | Refine; actual cancellation, latest artifacts and usage-extension controls. Early-stop credit return is a commercial policy decision. |
| HC-E07 | Fault tolerance | F12, F17 | Covered; bounded restart/retry, uncertain-effect reconciliation and no duplicate external writes. |
| HC-E08 | Coding/app creation | F12, F16 | Demonstrated scenario; validate authorized local build/test/artifact behavior, not arbitrary coding success. |
| HC-F01 | Integration catalog | F15 | Covered; connector-by-connector capabilities/scopes. Examples do not establish exhaustive current support. |
| HC-F02 | Multiple accounts | F15 | Covered; source-account attribution and explicit ambiguity handling within authorized read scope. |
| HC-F03 | Custom MCP | F15 | Strengthen with HC-T13; server authentication, schema discovery and explicit status transitions. |
| HC-F04 | Workspace workflows | F15, F12, F16 | Covered; turn examples into connector-specific acceptance with exact account/action authority. |
| HC-F05 | Web research | F12, F14, F16 | Covered; evidence-linked claims and valid source references. |
| HC-F06 | Spotify/media | F15, F13 | Historical demonstration lead; verify current integration path before promising supported playback. |
| HC-G01 | Specialized helpers | F09, F20, F21 | Covered; role setup, identity and persistent workspace. |
| HC-G02 | Long-lived workspaces | F09, F10, F11, F16, F17 | Covered; durable own state/queue/files and explicit usage model. |
| HC-G03 | Personal/task memory | F11 | Covered; source/scope/edit/export/delete. Historical filenames do not dictate our schema. |
| HC-G04 | History/search | F10, F16 | Refine; draft lifetime, read/unread and source-linked artifacts. |
| HC-G05 | Model/routing policy | F01, F09, F12 | Covered; capability/budget-based backend abstraction rather than fixed model names. |
| HC-H01 | Attachments/drop | F16, F19 | Covered; image/file-only messages, drop recovery and correct conversation destination. |
| HC-H02 | Document intelligence | F03, F16 | Strengthen with HC-T04; answer from full source rather than visible pixels. |
| HC-H03 | Output/previews | F16 | Refine; live Markdown changes, GIF/media support and drag-out. Keep active previews isolated from privileged IPC. |
| HC-H04 | Output clarity | F16 | Covered; useful file names, focused tables, provenance and format-specific quality checks. |
| HC-I01 | Contextual suggestions | F18, F15 | Covered; opt-in scoped reads, bounded recency, sources and no mutations before approval. |
| HC-I02 | Suggestion UX | F18, F22, F19 | Refine; adjust/skip, deduplication, quiet behavior and reduced reminders when ignored. |
| HC-I03 | Routines | F17, F12 | Refine; one catch-up, busy/offline/wake states and three-actual-failure pause. |
| HC-I04 | Routine/task context | F17, F10, F18 | Covered; same conversation, quiet results and original supporting sources. |
| HC-J01 | Screen privacy disclosure | F03, F23 | Covered; explicit app data-flow/retention policy; competitor policy is not independent verification. |
| HC-J02 | Cloud processing | F01, F23 | Covered; disclose processing destination; local UI/storage/STT do not imply fully local reasoning. |
| HC-J03 | Analytics/background reads | F18, F22, F23 | Covered; diagnostics default to content-free data, opt-in exports and declared research access. |
| HC-J04 | Plans/quotas/prices | F24 | Covered later in M7; choose our own economics. Competitor pricing/limits are dated research, not product defaults. |
| HC-J05 | Billing/account lifecycle | F23, F24, F25, F27 | Covered in release/commercial milestones; team/marketplace maturity remains separately qualified. |
| HC-J06 | OS/distribution | F26, F21, F25 | Covered; retain Windows as an early architecture constraint. Microphone, screen and automation permissions are separate capabilities. |

## Acceptance crosswalk: all 22 scenarios

These remain planned tests. Mapping does not constitute a passing result. Several strengthen an existing broad test rather than add a new subsystem.

| Imported test | Existing acceptance coverage | Addition / evidence needed |
| --- | --- | --- |
| HC-T01 Screen | A03, A04 | Three real applications, live target bounding box and two monitor scales; disambiguate repeated labels. |
| HC-T02 Spatial | A05 | Circle one of several similar controls; no accidental action. |
| HC-T03 Tutor | A06, A04 | Wrong click, delayed load, pause and verified step state. |
| HC-T04 Whole document | F03/F16 planned; A16 only broadly related | Dedicated new fixture: source page 25 while page 2 is visible; cite actual page. |
| HC-T05 Voice | A01, A02, A08 | Stream/interrupt/device switch/revoke/drop without stale callbacks. |
| HC-T06 Dictation | A07 | Explicit five-app matrix, clipboard restoration, terminal newline and cancellation. |
| HC-T07 Compose | A07, A11 | Context-correct draft inserted into selected field/account; no send. |
| HC-T08 Browser agent | A13, A16 | Valid cited product comparison, task-window ownership, permissioned purchases. |
| HC-T09 Native agent | A10, A16 | Verify actual folder/file result and tool receipts, not a completion sentence. |
| HC-T10 Concurrent agents | A09, A10 partially | Explicit simultaneous-run/stop-one fixture and file/grant/context isolation. |
| HC-T11 Approval | A11, A12 | Exact outbound payload review and revocation before a pending send. |
| HC-T12 Connectors | A11 | Two real authorized test accounts, account labels and correct destination. |
| HC-T13 Custom MCP | F15 planned; A19 partially | Dedicated real-server auth/schema test; saved token alone is insufficient. |
| HC-T14 Routine | A14 | Three actual failures pause; offline waiting does not consume that counter or duplicate effects. |
| HC-T15 Suggestion | A15 | Source-linked read-only sample, adjust then approve, no undisclosed monitoring. |
| HC-T16 Persistence | A10 | Actual restart/checkpoint recovery without replaying completed writes. |
| HC-T17 Usage ceiling | A19, A10 partially | Dedicated quota-exhaustion fixture retaining artifacts and a usable UI. |
| HC-T18 Memory | A17, A09 | User control, isolation and deletion from applicable stores/indexes. |
| HC-T19 Desktop UX | A03, A08, A18 | Real focus/call/capture behavior plus measured idle resource use. |
| HC-T20 Privacy | A20 partially | Capture-path instrumentation and local-state checks alongside scoped network evidence; distinguish capture, retention and transmission. |
| HC-T21 Cross-platform | A01–A20 platform acceptance policy | Repeat selected scenarios on every declared shipping OS; build/CI evidence is separate from native desktop acceptance. |
| HC-T22 Prompt injection | Development protocol/policy plan; A12 partially | Dedicated hostile email/PDF and exfiltration attempt; validate tool/policy decisions rather than model prose alone. |

## Recommendations that need project context

- **Windows:** the document defers it to a late differentiation phase. The user already selected Windows support, so its feasibility and native contracts remain early decisions. There is no new approval to reverse that scope.
- **Starting code:** its architecture discussion predates our pinned community-source assessment. The two-candidate adoption gate was completed on 17 October 2026, with native OpenClicky selected; see `FOUNDATION_DECISION.md`. Do not repeat whole-app decompilation or assume the original Swift prototype is the best base.
- **Development tools:** keep the lean Evolve/Context Mode/REA protocol. The attachment does not evaluate our existing environment, and its generic agent-assignment section does not replace it.
- **Onboarding and UI:** preserve functional results while designing original interactions. Four questions, three starter characters, a macOS notch and competitor artwork are not architecture requirements for every platform.
- **Refunds and performance:** a ten-second agent-credit refund is HeyClicky's billing policy; stopping an API request does not imply a provider refund. Advertised 450 ms onset, language counts, pace ranges and fifteen-step budgets need separate product choices and measured acceptance.
- **Local processing:** distinguish offline dictation/speech, local storage, vision, reasoning and tool execution. A local-only mode must accurately state which capabilities are available with no external calls.
- **Skills and recordings:** the skill marketplace/editor, teach-by-demonstration, shared-machine identity and enterprise policy are proposed enhancements. Preserve them in the backlog without promoting them to verified current parity or immediate implementation.
- **Encryption and deletion:** define coverage for app-owned state, caches, indexes and backups separately from user-exported documents; verify the promised behavior rather than claiming all files everywhere are encrypted/deleted.
- **Permission prompts:** scope grants to capabilities/actions and the actual user request. Microphone permission is not screen-capture permission; a broad computer-use grant cannot authorize an unrelated account action.

## Targeted source checks

The official [changelog](https://www.heyclicky.com/changelog) corroborates the document's fifteen-step walkthrough budget (v1.0.48), correction-learning window of about twenty seconds (v1.0.37), early-stop agent-message return within ten seconds (v1.0.53), and pause after three failed routine runs (v1.0.50). Later release notes explicitly exclude offline cases from that failure counter and suppress Home screenshots on typed turns. These are shipping claims, not fresh runtime measurements.

The declaration that all Instagram content was not reviewed remains accurate. Neither this file nor the prior summary closes the audiovisual audit. Historical app-library/model/pricing numbers remain versioned claims, not a promise of exhaustive current coverage.

## Result and next step

All 60 catalogue entries and 22 scenarios are now accounted for against our plan. This closes the missing-specification gap identified in RESEARCH_UPDATE.md. It adds precision and explicit fixtures rather than changing our overall architecture or authorizing implementation.

At the time of this crosswalk, the next development decision was the isolated
adoption/feasibility comparison of Prasanth OpenClicky and ClickyX. That decision
was completed on 17 October 2026; subsequent implementation and acceptance work
is tracked in `NEXT_STEPS.md` and `BUILD_STATUS.md`. No model or environment
setting was changed here.

## Current acceptance boundary — 19 October 2026

The current implementation PRs have fresh local evidence, but none of that
closes the 22 mapped product acceptance scenarios as a whole. PR #1 has passing
macOS unit/offline checks but still needs native capture permission and live Stop
acceptance. PR #8 has a passing macOS build and is included in the 714-test
integrated #8+#9 run; custom-colour persistence and Windows UI acceptance remain
open. PR #9 has passing integrated Swift tests and a WPF cross-build, but no
Windows host, real overlay comparison or measured performance result was
available. Keep these distinctions when translating the competitor crosswalk
into release claims; current heads and exact counts are in
[BUILD_STATUS.md](BUILD_STATUS.md).
