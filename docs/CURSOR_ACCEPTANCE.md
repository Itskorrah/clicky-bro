# Companion pointer — appearance, visibility and motion acceptance

**Implementation scope:** existing native SwiftUI/AppKit and Windows WPF overlays only. The original pointer language is retained; the new work makes the effects more restrained and constrains bubbles to each monitor. There is no browser cursor overlay and no new animation dependency.

## Changes in this branch

- The original pointer keeps its 16-point triangle geometry and spring/Bezier navigation behaviour. Only the colour glow/shadow intensity and radius are reduced; existing focus/click-through and guide controls are unchanged.
- The Mac uses `BubblePosition.center`, which clamps SwiftUI centre coordinates to the current display. Windows uses `OverlayBubbleGeometry.Offset` for WPF top-left coordinates.
- Welcome, navigation and caption bubbles are constrained horizontally and vertically. On extremely small displays, an oversized bubble is centred or anchored at zero; the remaining clipping is a documented physical constraint, not silent movement to another monitor.
- The Windows moving viewport, per-monitor DPI conversions, frame-driven spring, flight planner and display boundaries remain unchanged. A lower blur value can reduce paint cost, **but no performance improvement is claimed without device measurements**.
- A frame of rendering should not introduce a new system pointer, intercept clicks, or move focus.

## Evidence and acceptance matrix

| Scenario | Required verification |
| --- | --- |
| Screen centre | Text bubbles remain near pointer and do not cover the system cursor |
| Left/right/top/bottom edges | Bubbles stay within the active monitor where possible; no unexpected flip |
| Tiny display / big text | No crash, negative origin or inaccessible Stop instruction |
| Two monitors, mixed DPI | One buddy at a time, no duplicate or clipped jumps; compare 100%, 150% and 200% scales |
| 60/120/144 Hz | Capture comparable screen recordings and CPU/GPU/frame timings on real monitors; compare with the original commit |
| Rapid cursor movement | Smooth target tracking without a multi-frame lag or permanent drag |
| Navigation canceled / Escape / app closes | Pending bubble and flight visuals stop without stale late effects |
| Light/dark/custom tints | Bubble text remains readable and selected colour is applied consistently (theme feature is a separate draft PR) |
| Reduced motion | Functional state and guide Stop remain discoverable with effects disabled |
| VoiceOver/Narrator | Meaningful message/status labels; nothing requires hover alone |
| No activity | Avoid unnecessary CPU/GPU drain; log actual idle metrics before claiming optimisation |

### Local automated checks

Compile and run all available tests from a full source checkout. On macOS run `python3 scripts/check_local.py --native` with Xcode installed; on Windows run the appropriate xUnit suites with the .NET SDK. The new files `BubblePositionTests.swift` and `OverlayBubbleGeometryTests.cs` are included in their platform test trees.

**Isolated evidence:** the pure Swift `BubblePosition.swift` source was compiled under Swift 6.2.1 for Linux with warnings as errors and five directly relevant geometry assertions passed. This is **not** a successful macOS application build.

### Performance benchmark protocol

With the same hardware, OS build and recording settings, compare original vs changed software for:
- Overlay CPU/GPU idle after 60 seconds;
- pointer motion at normal/rapid speed for 30 seconds and percentage of frames missing the display's frame budget;
- first frame after screen/DPI change;
- blur/raster frame cost while navigation bubble is visible and animating;
- time from cancellation to no visible motion;
- whether other applications receive expected input normally.

Never claim measured 120 Hz smoothness, battery savings or compatibility from source changes alone.
