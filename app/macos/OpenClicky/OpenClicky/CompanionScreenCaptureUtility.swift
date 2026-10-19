import AppKit
import ScreenCaptureKit

struct CompanionScreenCapture {
    let imageData: Data
    let label: String
    let isCursorScreen: Bool
    let displayWidthInPoints: Int
    let displayHeightInPoints: Int
    let displayFrame: CGRect
    let screenshotWidthInPixels: Int
    let screenshotHeightInPixels: Int
}

struct CompanionWindowIdentity: Equatable, Sendable {
    let windowID: CGWindowID
    let processID: pid_t
}

enum CompanionScreenCaptureStopReason: String, Sendable {
    case userRequested
    case windowClosed
    case captureFailed
}

/// A local diagnostic records only whether a frame was delivered, never its pixels.
/// CGPreflightScreenCaptureAccess is a useful signal, not proof that ScreenCaptureKit works.
struct CompanionCaptureDiagnosis: Equatable {
    let permissionReported: Bool
    let hadSelectedWindow: Bool
    let frameCaptured: Bool
    let detail: String

    var summary: String {
        let permission = permissionReported ? "macOS reports Screen Recording allowed" : "macOS has not confirmed Screen Recording for this build"
        let selection = hadSelectedWindow ? "Selected window present" : "No window selected"
        let frame = frameCaptured ? "Local frame captured" : "No usable local frame"
        return "\(permission) · \(selection) · \(frame). \(detail)"
    }
}

/// Every model-facing capture is limited to one explicitly selected window.
/// Closing/moving the target never silently expands sharing to a display.
@MainActor
enum CompanionScreenCaptureUtility {
    private static var selection: CompanionWindowIdentity?
    private static var indicator: NSStatusItem?
    private static var activeWindowPicker: NSAlert?
    private static var isWindowPickerPresented = false
    private static let controls = SharingControls()

    nonisolated static func appKitFrame(for frame: CGRect, primaryMaxY: CGFloat) -> CGRect {
        CGRect(x: frame.minX, y: primaryMaxY - frame.maxY, width: frame.width, height: frame.height)
    }

    static func stopSharing(reason: CompanionScreenCaptureStopReason = .userRequested) {
        selection = nil
        if let indicator { NSStatusBar.system.removeStatusItem(indicator) }
        indicator = nil
        NotificationCenter.default.post(
            name: Notification.Name("clickyBroSharingStopped"),
            object: nil,
            userInfo: ["reason": reason.rawValue]
        )
    }

    nonisolated static func matchesSelectedWindow(
        _ selected: CompanionWindowIdentity?,
        windowID: CGWindowID,
        processID: pid_t
    ) -> Bool {
        selected == CompanionWindowIdentity(windowID: windowID, processID: processID)
    }

    static func cancelPendingWindowSelection() {
        guard activeWindowPicker != nil else { return }
        NSApp.abortModal()
    }

    /// The diagnostics button never opens a picker or sends image data to a provider.
    /// Preflight and an actual selected-window frame are independent observations.
    static func diagnoseSelectedWindow() async -> CompanionCaptureDiagnosis {
        let reported = CGPreflightScreenCaptureAccess()
        guard selection != nil else {
            return CompanionCaptureDiagnosis(permissionReported: reported, hadSelectedWindow: false,
                frameCaptured: false, detail: "Choose a window from the companion first, then test this exact app build.")
        }
        do {
            let frame = try await captureSelectedWindow()
            return CompanionCaptureDiagnosis(permissionReported: reported, hadSelectedWindow: true,
                frameCaptured: !frame.imageData.isEmpty,
                detail: "Received \(frame.screenshotWidthInPixels) × \(frame.screenshotHeightInPixels) pixels locally. Nothing was sent or saved.")
        } catch is CancellationError {
            return CompanionCaptureDiagnosis(permissionReported: reported, hadSelectedWindow: true,
                frameCaptured: false, detail: "The test was cancelled.")
        } catch {
            return CompanionCaptureDiagnosis(permissionReported: reported, hadSelectedWindow: true,
                frameCaptured: false, detail: "Capture failed: \(error.localizedDescription). Check this app’s Screen Recording entry, then quit and reopen.")
        }
    }

    nonisolated static func hasStableWindowFrame(before: CGRect, after: CGRect) -> Bool {
        before == after && hasFinitePositiveGeometry(before) && hasFinitePositiveGeometry(after)
    }

    private nonisolated static func hasFinitePositiveGeometry(_ frame: CGRect) -> Bool {
        frame.minX.isFinite && frame.minY.isFinite && frame.maxX.isFinite && frame.maxY.isFinite &&
            frame.width > 0 && frame.height > 0 && frame.width.isFinite && frame.height.isFinite
    }

    static func captureSelectedWindow() async throws -> CompanionScreenCapture {
        try Task.checkCancellation()
        let available: SCShareableContent
        do {
            available = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: true)
        } catch {
            guard !Task.isCancelled else { throw CancellationError() }
            if selection != nil { stopSharing(reason: .captureFailed) }
            throw error
        }
        try Task.checkCancellation()
        let ownPID = ProcessInfo.processInfo.processIdentifier
        let windows = Self.shareableWindows(in: available, excludingProcessID: ownPID)

        if let selection, !windows.contains(where: { Self.identity(of: $0) == selection }) {
            stopSharing(reason: .windowClosed)
            throw failure("The shared window is closed or unavailable. Choose a window again; nothing else was captured.")
        }

        if selection == nil {
            guard !windows.isEmpty else { throw failure("No shareable windows. Open a window and allow Screen Recording for clicky-bro.") }
            guard !isWindowPickerPresented else {
                throw failure("A window picker is already open. Finish or cancel it before asking again.")
            }
            let alert = NSAlert()
            alert.messageText = "Choose a window to share"
            alert.informativeText = "Only this window will be captured when you ask. Its images go to your chosen AI provider. Stop sharing from the menu bar."
            let picker = NSPopUpButton(frame: NSRect(x: 0, y: 0, width: 430, height: 28))
            picker.addItems(withTitles: windows.map { "\($0.owningApplication?.applicationName ?? "App") — \($0.title ?? "Window")" })
            alert.accessoryView = picker
            alert.addButton(withTitle: "Share window")
            alert.addButton(withTitle: "Cancel")
            NSApp.activate(ignoringOtherApps: true)
            isWindowPickerPresented = true
            activeWindowPicker = alert
            defer {
                if activeWindowPicker === alert { activeWindowPicker = nil }
                isWindowPickerPresented = false
            }
            let response = await withTaskCancellationHandler {
                alert.runModal()
            } onCancel: {
                Task { @MainActor in
                    guard activeWindowPicker === alert else { return }
                    NSApp.abortModal()
                }
            }
            try Task.checkCancellation()
            guard response == .alertFirstButtonReturn else { throw CancellationError() }
            try Task.checkCancellation()
            let selectedIndex = picker.indexOfSelectedItem
            guard windows.indices.contains(selectedIndex) else { throw CancellationError() }
            let chosen = windows[selectedIndex]
            guard let chosenIdentity = Self.identity(of: chosen) else { throw CancellationError() }
            selection = chosenIdentity
            NSRunningApplication(processIdentifier: chosenIdentity.processID)?.activate(options: [])
            showIndicator(name: chosen.owningApplication?.applicationName ?? "Window")
        }
        guard let selected = selection,
              let window = windows.first(where: { Self.identity(of: $0) == selected }) else {
            if selection != nil { stopSharing(reason: .windowClosed) }
            throw failure("The shared window is closed or unavailable. Choose a window again; nothing else was captured.")
        }
        let filter = SCContentFilter(desktopIndependentWindow: window)
        let configuration = SCStreamConfiguration()
        let ratio = min(1, 1280 / max(window.frame.width, window.frame.height))
        configuration.width = max(1, Int(window.frame.width * ratio))
        configuration.height = max(1, Int(window.frame.height * ratio))
        configuration.showsCursor = false
        configuration.ignoreShadowsSingleWindow = true
        let image: CGImage
        do {
            image = try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: configuration)
        } catch {
            guard !Task.isCancelled else { throw CancellationError() }
            stopSharing(ifMatching: selected, reason: .captureFailed)
            throw error
        }
        try Task.checkCancellation()
        guard Self.matchesSelectedWindow(selection, windowID: selected.windowID, processID: selected.processID) else {
            throw CancellationError()
        }

        let latestContent: SCShareableContent
        do {
            latestContent = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: true)
        } catch {
            guard !Task.isCancelled else { throw CancellationError() }
            stopSharing(ifMatching: selected, reason: .captureFailed)
            throw error
        }
        try Task.checkCancellation()
        guard Self.matchesSelectedWindow(selection, windowID: selected.windowID, processID: selected.processID) else {
            throw CancellationError()
        }
        let latestWindows = Self.shareableWindows(in: latestContent, excludingProcessID: ownPID)
        guard let latestWindow = latestWindows.first(where: { Self.identity(of: $0) == selected }) else {
            stopSharing(ifMatching: selected, reason: .windowClosed)
            throw failure("The shared window closed during capture. Choose a window again; nothing else was captured.")
        }
        guard Self.hasStableWindowFrame(before: window.frame, after: latestWindow.frame) else {
            throw failure("The shared window moved or resized during capture. Ask again for a fresh image.")
        }
        guard let data = NSBitmapImageRep(cgImage: image).representation(using: .jpeg, properties: [.compressionFactor: 0.8]) else {
            stopSharing(ifMatching: selected, reason: .captureFailed)
            throw failure("Could not encode the selected window.")
        }
        let rect = appKitFrame(for: latestWindow.frame, primaryMaxY: NSScreen.screens.first?.frame.maxY ?? 0)
        return CompanionScreenCapture(imageData: data, label: "Shared window: \(latestWindow.owningApplication?.applicationName ?? "App") — \(latestWindow.title ?? "Window")", isCursorScreen: true,
            displayWidthInPoints: Int(rect.width), displayHeightInPoints: Int(rect.height), displayFrame: rect,
            screenshotWidthInPixels: image.width, screenshotHeightInPixels: image.height)
    }

    /// Kept for existing native callers; its scope is still one selected window.
    static func captureAllScreensAsJPEG() async throws -> [CompanionScreenCapture] {
        [try await captureSelectedWindow()]
    }

    static func captureCursorScreenContext() async -> RealtimeScreenContext? {
        guard let capture = try? await captureSelectedWindow() else { return nil }
        let mouse = NSEvent.mouseLocation
        let x = Int((mouse.x - capture.displayFrame.minX) * CGFloat(capture.screenshotWidthInPixels) / max(capture.displayFrame.width, 1))
        let y = Int((capture.displayFrame.maxY - mouse.y) * CGFloat(capture.screenshotHeightInPixels) / max(capture.displayFrame.height, 1))
        return RealtimeScreenContext(jpeg: capture.imageData,
            caption: "\(capture.label). Image \(capture.screenshotWidthInPixels)x\(capture.screenshotHeightInPixels) pixels; pointer at (\(x), \(y)), which may be outside this window.", capture: capture)
    }

    private static func showIndicator(name: String) {
        if indicator == nil { indicator = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength) }
        indicator?.button?.title = "Window: \(name.prefix(20))"
        indicator?.button?.toolTip = "clicky-bro captures this selected window only when you ask"
        let menu = NSMenu()
        let stop = NSMenuItem(title: "Stop sharing window", action: #selector(SharingControls.stop), keyEquivalent: "")
        stop.target = controls
        menu.addItem(stop)
        indicator?.menu = menu
    }

    private static func shareableWindows(in content: SCShareableContent, excludingProcessID ownPID: pid_t) -> [SCWindow] {
        content.windows.filter { window in
            guard let application = window.owningApplication else { return false }
            return application.processID != ownPID && window.windowLayer == 0 &&
                window.frame.width >= 80 && window.frame.height >= 60 && !(window.title ?? "").isEmpty
        }.sorted {
            ($0.owningApplication?.applicationName ?? "") + ($0.title ?? "") <
                ($1.owningApplication?.applicationName ?? "") + ($1.title ?? "")
        }
    }

    private static func identity(of window: SCWindow) -> CompanionWindowIdentity? {
        guard let processID = window.owningApplication?.processID else { return nil }
        return CompanionWindowIdentity(windowID: window.windowID, processID: processID)
    }

    private static func stopSharing(ifMatching selected: CompanionWindowIdentity, reason: CompanionScreenCaptureStopReason) {
        guard matchesSelectedWindow(selection, windowID: selected.windowID, processID: selected.processID) else { return }
        stopSharing(reason: reason)
    }
    private static func failure(_ message: String) -> NSError {
        NSError(domain: "clicky-bro.capture", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
    }
}

@MainActor
private final class SharingControls: NSObject {
    @objc func stop() { CompanionScreenCaptureUtility.stopSharing() }
}
