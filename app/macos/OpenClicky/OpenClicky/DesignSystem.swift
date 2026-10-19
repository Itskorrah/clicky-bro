//
//  DesignSystem.swift
//  OpenClicky
//
//  The shared tokens the companion UI draws with: the overlay pointer and agent card colours, the
//  notch island's always-dark palette and sizes, the pointer cursor every button shows, and
//  `Color(hex:)`.
//

import SwiftUI
import AppKit

// MARK: - Design System Namespace

/// The top-level namespace for the design tokens.
/// Usage: `DS.Colors.overlayCursorColor`, `DS.HUD.text`, etc.
enum DS {

    // MARK: - Color Tokens

    enum Colors {

        /// The agent result card's status dot once the agent has answered.
        /// Adaptive user-selected accent; new installs and missing choices default to Navy Slate.
        /// A computed value matters: settings views redraw on @Published changes.
        static var accent: Color { userColour(companion: false) }

        /// Ink chosen to maintain readable contrast over the selected accent fill.
        static var accentText: Color {
            Color(nsColor: NSColor(name: nil) { appearance in
                let accent = preferredHex(companion: false, appearance: appearance)
                return NSColor(hex: ClickyThemePalette.textOnAccent(accent))
            })
        }

        static let lightCanvas = Color(hex: "#F6F8FA")
        static let darkCanvas = Color(hex: "#0D1117")
        static let lightSurface = Color(hex: "#FFFFFF")
        static let darkSurface = Color(hex: "#161B22")
        static let lightBorder = Color(hex: "#D0D7DE")
        static let darkBorder = Color(hex: "#30363D")

        private static func preferredHex(companion: Bool, appearance: NSAppearance) -> String {
            let preferences = UserDefaults.standard
            let selectedAppearance = DictationAppearance(
                rawValue: preferences.string(forKey: "dictation.appearance") ?? "") ?? .system
            let systemIsDark = appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua
            let dark = ClickyThemePalette.isDarkAppearance(selectedAppearance, systemIsDark: systemIsDark)
            let preset = preferences.string(forKey: "appearance.accentPreset") ?? ClickyThemePalette.defaultPresetID
            let customAccent = preferences.string(forKey: "appearance.customAccentHex") ?? ClickyThemePalette.defaultAccentHex
            let follow = preferences.object(forKey: "appearance.companionFollowsAccent") == nil
                ? true : preferences.bool(forKey: "appearance.companionFollowsAccent")
            let customCompanion = preferences.string(forKey: "appearance.customCompanionHex") ?? ClickyThemePalette.defaultAccentHex
            return companion
                ? ClickyThemePalette.resolveCompanion(
                    preset: preset, customAccentHex: customAccent,
                    followsAccent: follow, customCompanionHex: customCompanion, dark: dark)
                : ClickyThemePalette.resolve(preset: preset, customHex: customAccent, dark: dark)
        }

        private static func userColour(companion: Bool) -> Color {
            Color(nsColor: NSColor(name: nil) { appearance in
                NSColor(hex: preferredHex(companion: companion, appearance: appearance))
            })
        }
        static let canvas = adaptive(light: 0xF6F8FA, dark: 0x0D1117)
        static let surface = adaptive(light: 0xFFFFFF, dark: 0x161B22)
        static let surfaceRaised = adaptive(light: 0xF6F8FA, dark: 0x21262D)
        static let primaryText = adaptive(light: 0x1F2328, dark: 0xE6EDF3)
        static let secondaryText = adaptive(light: 0x59636E, dark: 0xA1AAB4)
        static let tertiaryText = adaptive(light: 0x66707A, dark: 0x8B949E)
        static let border = adaptive(light: 0xD0D7DE, dark: 0x30363D)

        /// Semantic colours follow this window's effective NSAppearance, including system dark mode.
        private static func adaptive(light: UInt32, dark: UInt32) -> Color {
            Color(nsColor: NSColor(name: nil) { appearance in
                let value = appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? dark : light
                return NSColor(srgbRed: CGFloat((value >> 16) & 0xff) / 255,
                               green: CGFloat((value >> 8) & 0xff) / 255,
                               blue: CGFloat(value & 0xff) / 255, alpha: 1)
            })
        }

        /// The agent result card's status dot while the companion is still working.
        static let warning = Color(hex: "#FFB224")            // Radix Amber 9

        // ── Overlay Cursor ───────────────────────────────────────────

        /// The cursor/bubble color used in OverlayWindow.
        /// Kept distinct from the accent since it serves a different purpose
        /// (screen overlay vs in-app UI).
        static var overlayCursorColor: Color { userColour(companion: true) }

        /// A pale custom pointer needs dark text; a dark custom pointer needs white text.
        static var overlayCursorText: Color {
            Color(nsColor: NSColor(name: nil) { appearance in
                let accent = preferredHex(companion: true, appearance: appearance)
                return NSColor(hex: ClickyThemePalette.textOnAccent(accent))
            })
        }
    }

    // MARK: - HUD (the notch island, always dark)

    /// The refinement sheet's "HUD · always dark" palette and control sizes. The island does not
    /// follow the system appearance: it is part of the notch.
    enum HUD {
        static let island = Color(hex: "#0D1117")
        /// Pills and the gear in the band, a step lighter than the island.
        static let bandControl = Color(hex: "#161B22")
        static let surfaceRaised = Color(hex: "#21262D")
        /// The (i) button and other secondary squares on a surface.
        static let surfaceRaisedSoft = Color(hex: "#30363D")
        static let text = Color(hex: "#FFFFFF")
        static let text2 = Color(hex: "#C9D1D9")
        static let text3 = Color(hex: "#A1AAB4")
        static let pointer = Color(hex: "#80A9D4")
        /// The "!" disc behind a permission card's mark.
        static let pointerTint = Color(hex: "#1C2C3D")
        static let live = Color(hex: "#34C77B")

        static let pillHeight: CGFloat = 24
        static let tileSize: CGFloat = 40
        static let minimumHitSize: CGFloat = 22
        static let tileRadius: CGFloat = 10
        static let islandRadius: CGFloat = 22
        static let bodySidePadding: CGFloat = 16
        static let stripWidth: CGFloat = 380
        static let stripHeight: CGFloat = 37
    }
}

/// Convert a validated six-digit RGB hex into a native dynamic appearance colour.
private extension NSColor {
    convenience init(hex: String) {
        let raw = Int(hex.dropFirst(), radix: 16) ?? 0x2B547B
        self.init(srgbRed: CGFloat((raw >> 16) & 255) / 255,
                  green: CGFloat((raw >> 8) & 255) / 255,
                  blue: CGFloat(raw & 255) / 255, alpha: 1)
    }
}

// MARK: - Pointer Cursor

extension View {
    /// Attaches the shared pointing-hand cursor treatment used across interactive controls.
    /// Disabled controls can opt out so they keep the default arrow cursor.
    func pointerCursor(isEnabled: Bool = true) -> some View {
        self.overlay {
            if isEnabled {
                PointerCursorView()
            }
        }
    }
}

// MARK: - Pointer Cursor (AppKit Bridge)

/// Uses AppKit's cursor rect system to reliably show a pointing hand cursor.
/// More reliable than NSCursor.push()/pop() inside SwiftUI's .onHover because
/// cursor rects are managed at the window level and don't conflict with
/// SwiftUI's internal cursor handling.
private class PointerCursorNSView: NSView {
    override func resetCursorRects() {
        super.resetCursorRects()
        addCursorRect(bounds, cursor: .pointingHand)
    }

    override func hitTest(_ point: NSPoint) -> NSView? {
        return nil
    }
}

private struct PointerCursorView: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        return PointerCursorNSView()
    }

    func updateNSView(_ nsView: NSView, context: Context) {
        // Invalidate cursor rects when the view updates (e.g., resizes)
        // so AppKit recalculates the cursor area.
        nsView.window?.invalidateCursorRects(for: nsView)
    }
}

// MARK: - Color Utilities

extension Color {
    /// Create a Color from a hex string like "#FF5733" or "FF5733".
    init(hex: String) {
        let hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "#", with: "")

        var rgbValue: UInt64 = 0
        Scanner(string: hexSanitized).scanHexInt64(&rgbValue)

        let red = Double((rgbValue & 0xFF0000) >> 16) / 255.0
        let green = Double((rgbValue & 0x00FF00) >> 8) / 255.0
        let blue = Double(rgbValue & 0x0000FF) / 255.0

        self.init(red: red, green: green, blue: blue)
    }
}
