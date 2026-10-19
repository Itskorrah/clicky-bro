import Foundation

/// Native, dependency-free theme calculations. User preferences store only small
/// preset IDs and validated RGB hex strings; invalid saved values fail closed.
enum ClickyThemePalette {
    static let defaultPresetID = "navy"
    static let defaultAccentHex = "#2B547B"
    static let presets: [(id: String, title: String)] = [
        ("navy", "Navy Slate"), ("coral", "Classic Coral"), ("azure", "Azure Blue"),
        ("emerald", "Emerald"), ("violet", "Violet"),
        ("graphite", "Graphite"), ("custom", "Custom")
    ]

    static func normalizedHex(_ input: String?) -> String? {
        guard let input else { return nil }
        let cleaned = input.trimmingCharacters(in: .whitespacesAndNewlines)
        let raw = cleaned.hasPrefix("#") ? String(cleaned.dropFirst()) : cleaned
        guard raw.utf8.count == 6,
              raw.unicodeScalars.allSatisfy({ CharacterSet(charactersIn: "0123456789ABCDEFabcdef").contains($0) })
        else { return nil }
        return "#" + raw.uppercased()
    }

    static func isDarkAppearance(_ appearance: DictationAppearance, systemIsDark: Bool) -> Bool {
        switch appearance {
        case .light: return false
        case .dark: return true
        case .system: return systemIsDark
        }
    }

    static func resolve(preset: String, customHex: String, dark: Bool) -> String {
        let original: String
        switch preset {
        case "navy": original = dark ? "#80A9D4" : defaultAccentHex
        case "coral": original = dark ? "#E8653F" : "#D24E2A"
        case "azure": original = dark ? "#60A5FA" : "#2563EB"
        case "emerald": original = dark ? "#34D399" : "#047857"
        case "violet": original = dark ? "#A78BFA" : "#6D28D9"
        case "graphite": original = dark ? "#CBD5E1" : "#475569"
        case "custom": original = normalizedHex(customHex) ?? (dark ? "#80A9D4" : defaultAccentHex)
        default: original = dark ? "#80A9D4" : defaultAccentHex
        }
        return ensureContrast(original, against: dark ? "#21262D" : "#F6F8FA", dark: dark)
    }

    static func resolveCompanion(preset: String, customAccentHex: String,
                                 followsAccent: Bool, customCompanionHex: String,
                                 dark: Bool) -> String {
        if followsAccent { return resolve(preset: preset, customHex: customAccentHex, dark: dark) }
        let colour = normalizedHex(customCompanionHex) ?? defaultAccentHex
        return ensureContrast(colour, against: dark ? "#21262D" : "#F6F8FA", dark: dark)
    }

    /// Dynamic on-accent text; white on a pale blue pointer fails contrast in dark mode.
    static func textOnAccent(_ accent: String) -> String {
        contrast("#FFFFFF", accent) >= contrast("#0F172A", accent) ? "#FFFFFF" : "#0F172A"
    }

    static func contrast(_ first: String, _ second: String) -> Double {
        let a = luminance(first), b = luminance(second)
        return (max(a, b) + 0.05) / (min(a, b) + 0.05)
    }

    private static func luminance(_ hex: String) -> Double {
        let value = Int(hex.dropFirst(), radix: 16) ?? 0
        func channel(_ n: Int) -> Double {
            let x = Double(n) / 255.0
            return x <= 0.04045 ? x / 12.92 : pow((x + 0.055) / 1.055, 2.4)
        }
        return 0.2126 * channel((value >> 16) & 255) +
               0.7152 * channel((value >> 8) & 255) +
               0.0722 * channel(value & 255)
    }

    private static func ensureContrast(_ hex: String, against background: String, dark: Bool) -> String {
        if contrast(hex, background) >= 4.5 { return hex }
        let value = Int(hex.dropFirst(), radix: 16) ?? 0
        let original = [(value >> 16) & 255, (value >> 8) & 255, value & 255]
        for step in 1...100 {
            let fraction = Double(step) / 100.0
            let target = dark ? 255.0 : 0.0
            let rgb = original.map { Int((Double($0) + (target - Double($0)) * fraction).rounded()) }
            let candidate = String(format: "#%02X%02X%02X", rgb[0], rgb[1], rgb[2])
            if contrast(candidate, background) >= 4.5 { return candidate }
        }
        return dark ? "#FFFFFF" : "#000000"
    }
}
