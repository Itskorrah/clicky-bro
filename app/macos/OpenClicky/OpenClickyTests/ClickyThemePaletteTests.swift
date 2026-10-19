import Foundation
import Testing
@testable import OpenClicky

struct ClickyThemePaletteTests {
    @Test func presetsAlwaysMeetReadableContrastInBothAppearances() {
        for preset in ClickyThemePalette.presets {
            for dark in [false, true] {
                let resolved = ClickyThemePalette.resolve(preset: preset.id, customHex: "#FFFFFF", dark: dark)
                #expect(ClickyThemePalette.contrast(resolved, dark ? "#202329" : "#FFFFFF") >= 4.5)
            }
        }
    }

    @Test func hexInputValidationAndDefaultCompatibility() {
        #expect(ClickyThemePalette.normalizedHex(" abcdef ") == "#ABCDEF")
        #expect(ClickyThemePalette.normalizedHex("#12345") == nil)
        #expect(ClickyThemePalette.normalizedHex("#00000000") == nil)
        #expect(ClickyThemePalette.resolve(preset: "invalid", customHex: "", dark: false)
            == ClickyThemePalette.resolve(preset: "coral", customHex: "", dark: false))
    }

    @Test func companionColourCanBeIndependent() {
        let standard = ClickyThemePalette.resolve(preset: "azure", customHex: "#FF00FF", dark: true)
        let following = ClickyThemePalette.resolveCompanion(
            preset: "azure", customAccentHex: "#FF00FF", followsAccent: true,
            customCompanionHex: "#00FF00", dark: true)
        #expect(following == standard)
        let independent = ClickyThemePalette.resolveCompanion(
            preset: "azure", customAccentHex: "#FF00FF", followsAccent: false,
            customCompanionHex: "#00FF00", dark: true)
        #expect(independent != following)
    }

    @Test @MainActor func newSettingsDefaultToClassicAndKeepTheExistingAppearance() {
        let key = "clicky-theme-tests-\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: key)!
        defer { defaults.removePersistentDomain(forName: key) }
        let settings = DictationSettings(defaults: defaults)
        #expect(settings.appearance == .system)
        #expect(settings.accentPreset == "coral")
        #expect(settings.companionFollowsAccent)
        settings.accentPreset = "violet"
        settings.customAccentHex = "#123ABC"
        settings.companionFollowsAccent = false
        settings.customCompanionHex = "#CDEF12"
        #expect(defaults.string(forKey: "appearance.accentPreset") == "violet")
        #expect(defaults.string(forKey: "appearance.customCompanionHex") == "#CDEF12")
    }
}
