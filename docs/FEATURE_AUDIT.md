# HeyClicky feature and public-source audit

Research date: 17 October 2026. This is an evidence-backed planning baseline, not a runtime acceptance report.

The public repository is a useful teaching-assistant prototype. It is not the source of the current commercial application. Its README explicitly identifies the April 2026 public/private split. Building the current feature set requires substantial new engineering rather than rebranding this repository.

## Evidence and coverage

| ID | Evidence type | Scope |
|---|---|---|
| WEB-H | First-party product claims | [Home, pricing and FAQ](https://www.heyclicky.com/), fetched live |
| WEB-C | First-party release claims | [Complete published changelog](https://www.heyclicky.com/changelog), v1.0 through v1.0.53, reviewed across all release sections |
| WEB-T | First-party processing claims | [Trust](https://www.heyclicky.com/trust) |
| WEB-P | First-party policy | [Privacy policy](https://www.heyclicky.com/privacy-policy) |
| WEB-R | First-party commercial terms | [Referral program](https://www.heyclicky.com/referral-terms) |
| WEB-A | First-party background | [About](https://www.heyclicky.com/about) and [careers](https://www.heyclicky.com/careers) |
| SRC | Static source | [farzaa/clicky at a80fa80721a8aebe51a170a7780705024ebc6e46](https://github.com/farzaa/clicky/tree/a80fa80721a8aebe51a170a7780705024ebc6e46), freshly cloned |
| ART | Static installed artifact | Separate REA investigation; see REA setup and architecture report |
| PROP | Original proposal | Our proposed acceptance criteria and improvements; not claims about HeyClicky's implementation |

Website coverage includes all seven sitemap routes: home, changelog, trust, about, careers, privacy policy and referral terms. Features and pricing navigation points into the home page. External social videos, private account screens, checkout, connector authorizations, referrals and real tasks were not exercised. The careers page advertises mobile work; it does not establish that a mobile product exists. About's dated timeline and the changelog's initial-release dates differ, so this audit uses versioned releases as the feature chronology.

Local research materials live under `.local/research/`, which is excluded from Git. The website manifest records fetched URLs/statuses; downloaded HTML preserves the observed first-party pages. The source clone is research material, not the new application's scaffold. The source tree has 22 main-target Swift files, approximately 7,659 lines, an Xcode project, a small Worker, release scripts, assets and tests. The line total includes comments and blank lines.

No application was launched by this feature audit. No microphone, screen, connector, account, payment or paid inference flow was used. A feature marked public-source present means code exists; it does not mean it was built or accepted on this Mac.

## Feature matrix

The commercial column below is a compact inventory of first-party claims, mainly WEB-C. “Absent” means no corresponding subsystem was found in this pinned public source tree; private implementations are outside that tree. Current behavior remains untested.

| Claim | Capability | Public-source baseline | Commercial claim / source |
|---|---|---|---|
| F01 | Voice | Push-to-talk audio/provider abstraction [S01, S02] | Realtime, interruption [WEB-C] |
| F02 | Voice controls | Fixed modifier gesture, waveform [S02] | Voices, speed, shortcuts [WEB-C] |
| F03 | Screen context | Multi-display JPEG capture [S03] | Whole-document reading [WEB-C] |
| F04 | Teaching | Coordinate tag, animated pointing [S04] | Drawings, click-aware walkthroughs [WEB-C] |
| F05 | Spatial input | Not found | User scribbles [WEB-C] |
| F06 | Text | Response bubble | Composer, selectable replies [WEB-C] |
| F07 | Dictation | Capture-to-assistant callback [S02] | Cross-app insertion, dictionary [WEB-C] |
| F08 | Contextual writing | Screenshot-aware response [S01] | Screen-aware drafting [WEB-C] |
| F09 | Agents | Not found | Persistent named agents [WEB-C] |
| F10 | Conversations | Ten in-memory exchanges [S05] | Search, archive, pins [WEB-C] |
| F11 | Memory | Settings persist; history does not [S05] | User/agent memory [WEB-C] |
| F12 | Task lifecycle | Cancel current response | Progress, follow-ups, retries [WEB-C] |
| F13 | Computer control | Overlay points; no action engine | Consent-scoped native driver [WEB-C] |
| F14 | Browsing | Not found | Separate task windows [WEB-C] |
| F15 | Connected tools | Not found | Catalog, custom MCP, multiple accounts [WEB-C] |
| F16 | Files | No agent artifact pipeline | Attachments, generation, previews [WEB-C] |
| F17 | Routines | Not found | Local scheduling, recovery [WEB-C] |
| F18 | Suggestions | Not found | Connected-app research, approval [WEB-C] |
| F19 | Home | Menu-bar panel, cursor overlay [S06] | Notch, pop-out, resizing [WEB-C] |
| F20 | Personalization | Limited persisted choices | Characters, colors [WEB-C] |
| F21 | Onboarding | Email, permissions, demo [S06] | Interview, personalized agents [WEB-C] |
| F22 | Quiet behavior | Limited interaction visibility | Calls, sharing, Focus [WEB-C] |
| F23 | Accounts | Email identification only [S07] | Sign-in, deletion [WEB-H, WEB-P] |
| F24 | Commercial systems | Not found | Plans, quotas [WEB-H]; teams [WEB-C] |
| F25 | Distribution | Release scripts; inactive updater [S08] | In-app updates [WEB-C] |
| F26 | Platform | AppKit/SwiftUI, macOS | macOS; Windows waitlist [WEB-H] |
| F27 | Referrals | Not found | Referral dashboard/payouts [WEB-R] |

Historical/current distinctions: community Skills paused in v1.0.49; HeyClicky Notes removed in v1.0.21; activity-tracking suggestions removed in v1.0.46, distinct from today's connected-app suggestions. Agent cursor removed in v1.0.52; teaching overlays remain. Reddit/Monday connections paused in v1.0.53. Always-on was experimental/headphones-limited; current availability needs runtime checking. [WEB-C]

The home page advertises a free tier, Pro at $20/month and Max at $100/month, with agent-message allowances of 25, 150 and 1,000 respectively. Currency localization and actual checkout were not tested. The “free” download headline should not be treated as unlimited free service. [WEB-H]

## Verified public-source anchors

All links in this section pin the audited commit; source evidence may differ from current installed HeyClicky.

| ID | Finding | Primary source |
|---|---|---|
| S00 | README says existing source remains open, newer development private; MIT permits redistribution/commercial use subject to notice | [README](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/README.md), [LICENSE](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/LICENSE) |
| S01 | Active main pipeline constructs Claude/ElevenLabs clients through a configurable Worker URL, captures displays, passes images plus history, streams reply, parses pointing, then plays TTS | [CompanionManager.swift:71](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L71), [586](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L586) |
| S02 | Dictation uses callback interfaces, AVAudioEngine and a selected provider; fallback selection happens at configuration time, not an observed runtime failover guarantee | [BuddyDictationManager.swift:213](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/BuddyDictationManager.swift#L213), [BuddyTranscriptionProvider.swift:39](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/BuddyTranscriptionProvider.swift#L39) |
| S03 | Capture sorts displays, identifies cursor display, excludes its own windows, resizes to a maximum dimension of 1280, labels each screenshot and returns screen/image dimensions for mapping | [CompanionScreenCaptureUtility.swift:30](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionScreenCaptureUtility.swift#L30) |
| S04 | Prompted POINT tags drive screenshot-pixel→display-point coordinate conversion; overlay is click-through, all-Spaces and animated. Pointing is guidance, not native computer control | [CompanionManager.swift:650](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L650), [OverlayWindow.swift:27](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/OverlayWindow.swift#L27), [491](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/OverlayWindow.swift#L491) |
| S05 | History is an ordinary array capped to ten user/assistant exchanges. Selected model, cursor preference and onboarding flags use UserDefaults | [CompanionManager.swift:83](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L83), [110](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L110), [684](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L684) |
| S06 | Menu-bar-only entry, custom panels, permission/onboarding UI. Model picker rendered once ready; cursor-toggle rendering commented out | [Info.plist:5](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/Info.plist#L5), [CompanionPanelView.swift:28](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionPanelView.swift#L28), [52](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionPanelView.swift#L52) |
| S07 | Transcript and assistant response included in PostHog event properties; email identifies the user; transcript also printed to console | [ClickyAnalytics.swift:83](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/ClickyAnalytics.swift#L83), [CompanionManager.swift:153](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L153), [522](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/CompanionManager.swift#L522) |
| S08 | Sparkle is linked and updater method exists, but launch invocation is commented; startup attempts login-item registration whenever status is not enabled | [leanring_buddyApp.swift:52](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/leanring_buddyApp.swift#L52), [63](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/leanring_buddyApp.swift#L63) |
| S09 | Worker exposes POST chat/TTS/temp-token forwarding without incoming user authentication, rate limiting, size limits or a request schema; upstream API keys are server-side | [worker/src/index.ts:19](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/worker/src/index.ts#L19), [51](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/worker/src/index.ts#L51) |
| S10 | AssemblyAI default uses 16kHz PCM and u3-rt-pro; Apple Speech requests on-device recognition when supported. Optional OpenAI transcription reads a bundle key and calls OpenAI directly | [AssemblyAIStreamingTranscriptionProvider.swift:448](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/AssemblyAIStreamingTranscriptionProvider.swift#L448), [AppleSpeechTranscriptionProvider.swift:90](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/AppleSpeechTranscriptionProvider.swift#L90), [OpenAIAudioTranscriptionProvider.swift:20](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/OpenAIAudioTranscriptionProvider.swift#L20), [181](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddy/OpenAIAudioTranscriptionProvider.swift#L181) |
| S11 | Three focused permission tests; remaining UI/launch files are mostly starter scaffolding, not feature acceptance coverage | [unit tests](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddyTests/leanring_buddyTests.swift), [UI tests](https://github.com/farzaa/clicky/blob/a80fa80721a8aebe51a170a7780705024ebc6e46/leanring-buddyUITests/leanring_buddyUITests.swift) |

Two older classes, `OpenAIAPI` and `ElementLocationDetector`, implement direct provider requests, but no instantiations were found in the 22 Swift source modules. Their existence is not evidence that the active voice path uses them. Similarly the public transcription-provider abstraction does not establish that the current shipped app uses AssemblyAI. Installed-artifact findings take precedence for present packaging, and runtime traces would be required for live routing.

The public root AGENTS document is broadly useful for the prototype; the nested app AGENTS document refers to source files that are no longer in this tree. Treat both as engineering documentation to check against code. In particular, “all APIs are proxied” is broader than the optional OpenAI transcription implementation actually supports.

## Privacy and reuse boundaries

WEB-T says model processing is cloud based, raw screenshots are not retained, generated screenshot analysis and prompts are retained, and connected apps can be read daily for suggestions while the app is open; that read can be disabled. It describes no other background activity tracking and no background service after quit. These are provider assertions, not findings from a packet capture or server audit.

WEB-P lists Anthropic, OpenAI, Deepgram and Cerebras, says screenshots/voice are captured locally before proxy transmission, and discusses retention/deletion including a stated 14-day response period with exceptions. The trust page names fewer AI providers. An implementation and data-flow audit is needed before treating the pages as an exhaustive processor inventory. Neither page proves that current analytics omit all conversation text; S07 proves the opposite only for the old public code. Do not transfer that old-code finding into an allegation about the commercial build.

The MIT grant applies to the published software, with its notice condition. Preserve attribution for material reused code. The README's permission to build companies from that source is unusually explicit. It does not establish that later private application code, hosted services, marks or proprietary bundled material have the same grant. Maintain a provenance ledger for reused modules and dependencies; create our own branding, interface assets, prompts and unlicensed implementation. This is a concrete engineering boundary, not an assertion that reverse engineering recovers a licence to redistribute private code.

WEB-R provides a referral system with commissions, attribution windows, reversals and manually arranged payouts. This belongs to a future commercial platform, not the core local assistant. Replicating every marketing feature before validating the assistant would increase scope without improving the first user workflow.

## Proposed acceptance backlog (PROP)

These are our own test cases for the new product. They turn the feature inventory into reviewable work without claiming that HeyClicky passes them.

| Acceptance ID | Proposed scenario | Required evidence |
|---|---|---|
| A01 | Invoke from another app, speak once, release, receive a response, cancel midway | Timestamped local trace; no duplicate turns; cancelled response cannot reappear |
| A02 | Deny microphone, deny screen access, revoke each after granting, retry | Correct settings guidance; useful text-only path; no frozen interaction |
| A03 | Use two screens with different scale factors and negative origins; rearrange them mid-session | Target coordinate logs plus actual overlay captures on each platform |
| A04 | Point at an element, move the underlying window, request the next step | Fresh observation or uncertainty indication; stale coordinates cannot trigger action |
| A05 | Draw a circle around one of several similar controls | Saved synthetic test input and localized answer; no full-session screenshot retention by default |
| A06 | Execute a long guided procedure, do one step manually, continue after an interruption | Goal and completed steps remain correct; repeated failure changes the next instruction |
| A07 | Dictate into browser, Electron editor, native editor and terminal | Exact target field, faithful text, clipboard restoration, no accidental command execution |
| A08 | Switch microphone/headphones, close lid, interrupt with a call | Recoverable audio state and retained transcript; no main-thread freeze |
| A09 | Create two workers with distinct scopes, speak an ambiguous follow-up | Correct routing or a short clarification; work cannot silently cross scopes |
| A10 | Stop a task while a tool is pending, then resume/retry after restart | Durable state, explicit tool outcome, no duplicated external write |
| A11 | Add two accounts of one integration and request an ambiguous new send | Account shown and explicitly selected; credentials never reach prompts/logs |
| A12 | Reject computer access, then allow one conversation and spawn a helper | Denial enforced outside the prompt; consent propagates only to authorized work |
| A13 | User keeps typing while background browser work executes | No real-pointer theft; target window identity verified before every mutation |
| A14 | Schedule a routine, sleep through several runs, wake offline, reconnect | At most one catch-up, bounded retries, clear paused/queued state |
| A15 | Generate suggestions with a read-only connector scope | Research cannot mutate; approval required before work; disable revokes future checks |
| A16 | Make files, attach files, open previews, switch chats, regenerate | Per-turn artifact provenance; no stale results; unsupported format opens safely |
| A17 | Ask assistant what it remembers, edit it, delete it, export it | Inspectable memory provenance, scope and persistence with confirmed deletion |
| A18 | Install update, reject auto-start, relaunch and quit | Preference respected, signed updater path, process cleanup verified |
| A19 | Simulate slow provider, disconnected MCP, quota denial and corrupt state | Typed error categories, bounded retries, recoverable UI; no invented success |
| A20 | Inspect diagnostics after voice/screens/connector use | Content absent by default; redaction tests; opt-in export previews exactly what is shared |

## Product opportunities (PROP)

The strongest differentiator is dependable help in the active task, with an understandable record of what it saw and did. Prioritize reliable execution, inspectable memory, explicit per-task authority and recovery before adding a large connector catalog.

Recommended additions are a preview of screen/region context before transmission, per-app exclusions, a private text-only/local mode where feasible, visible task cost limits, exportable local history, a memory editor with source links and expiry, and action receipts with before/after evidence. Support keyboard-only use and a reduced-motion alternative to the animated companion. Treat local model quality and laptop resource use as measured experiments rather than promises.

Build integration and computer-use access through a policy boundary owned by our application, independent of model instructions. A connector's “read-only” label must match actual allowed methods; task cancellation must invalidate pending authority; authorization must be scoped to accounts, targets and operations. Start with a few well-tested tools and a documented connector contract, then expand.

The existing MIT code can inform capture geometry, audio lifecycle and overlays. A Mac/Windows product should establish platform interfaces for capture, permissions, global shortcuts, text insertion, accessibility, windows and audio before selecting how much Swift to retain. Windows parity requires real Windows execution evidence, not only a successful cross-platform frontend build.

## Outstanding uncertainties

- Exact currently enabled models and provider routing, not merely catalog entries or historical releases.
- Current always-on mode and its capture semantics, including how hotkey-only marketing describes a long running walkthrough or agent.
- Complete active connector catalog, per-connector scopes, browser/runtime compatibility and remote backend behavior.
- Current memory storage/encryption/synchronization, deletion propagation, recovery behavior and data export completeness.
- Real latency, idle CPU/RAM, battery usage, background-control correctness and permission enforcement.
- Actual Windows hardware acceptance for our future implementation.

These require an explicit controlled runtime session, with disposable documents/accounts and a known task set. Static source and artifacts can narrow the questions; they cannot replace those measurements.
