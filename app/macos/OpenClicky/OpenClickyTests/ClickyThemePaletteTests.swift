import Foundation
import Testing
@testable import OpenClicky

struct ClickyThemePaletteTests {
    @Test func azurePresetMatchesManifestInBothAppearances() {
        let azure = [false: "#2563EB", true: "#60A5FA"]
        for (dark, expected) in azure {
            let resolved = ClickyThemePalette.resolve(preset: "azure", customHex: "#FFFFFF", dark: dark)
            #expect(resolved == expected)
            #expect(ClickyThemePalette.resolveCompanion(
                preset: "azure", customAccentHex: "#FFFFFF", followsAccent: true,
                customCompanionHex: "#000000", dark: dark) == expected)
            #expect(ClickyThemePalette.contrast(resolved, dark ? "#21262D" : "#F6F8FA") >= 4.5)
        }
    }

    @Test func navySlateIsTheNewInstallDefaultAndMatchesBothAppearanceSurfaces() {
        #expect(ClickyThemePalette.defaultPresetID == "navy")
        #expect(ClickyThemePalette.presets.contains(where: { $0.id == "coral" }))
        #expect(ClickyThemePalette.resolve(preset: "navy", customHex: "#FFFFFF", dark: false) == "#2B547B")
        #expect(ClickyThemePalette.resolve(preset: "navy", customHex: "#FFFFFF", dark: true) == "#80A9D4")
        #expect(ClickyThemePalette.resolve(preset: "navy", customHex: "#FFFFFF", dark: false)
            != ClickyThemePalette.resolve(preset: "coral", customHex: "#FFFFFF", dark: false))
        #expect(ClickyThemePalette.contrast("#2B547B", "#F6F8FA") >= 4.5)
        #expect(ClickyThemePalette.contrast("#80A9D4", "#21262D") >= 4.5)
    }

    @Test func presetsAlwaysMeetReadableContrastInBothAppearances() {
        for preset in ClickyThemePalette.presets {
            for dark in [false, true] {
                let resolved = ClickyThemePalette.resolve(preset: preset.id, customHex: "#FFFFFF", dark: dark)
                #expect(ClickyThemePalette.contrast(resolved, dark ? "#21262D" : "#F6F8FA") >= 4.5)
                #expect(ClickyThemePalette.contrast(
                    ClickyThemePalette.textOnAccent(resolved), resolved) >= 4.5)
            }
        }
    }

    @Test func hexInputValidationAndDefaultCompatibility() {
        #expect(ClickyThemePalette.normalizedHex(" abcdef ") == "#ABCDEF")
        #expect(ClickyThemePalette.normalizedHex("#12345") == nil)
        #expect(ClickyThemePalette.normalizedHex("#00000000") == nil)
        #expect(ClickyThemePalette.resolve(preset: "invalid", customHex: "", dark: false)
            == ClickyThemePalette.resolve(preset: "navy", customHex: "", dark: false))
        for dark in [false, true] {
            #expect(ClickyThemePalette.resolveCompanion(
                preset: "navy", customAccentHex: "", followsAccent: false,
                customCompanionHex: "invalid", dark: dark)
                == (dark ? "#7590A9" : ClickyThemePalette.defaultAccentHex))
        }
    }

    @Test func selectedAppearanceOverridesTheSystemOnlyForLightAndDark() {
        #expect(ClickyThemePalette.isDarkAppearance(.dark, systemIsDark: false))
        #expect(!ClickyThemePalette.isDarkAppearance(.light, systemIsDark: true))
        #expect(ClickyThemePalette.isDarkAppearance(.system, systemIsDark: true))
        #expect(!ClickyThemePalette.isDarkAppearance(.system, systemIsDark: false))
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

    @Test @MainActor func newSettingsDefaultToNavyAndKeepTheExistingAppearance() {
        let key = "clicky-theme-tests-\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: key)!
        defer { defaults.removePersistentDomain(forName: key) }
        let settings = DictationSettings(defaults: defaults)
        #expect(settings.appearance == .system)
        #expect(settings.accentPreset == "navy")
        #expect(settings.customAccentHex == "#2B547B")
        #expect(settings.companionFollowsAccent)
        #expect(settings.customCompanionHex == "#2B547B")
        settings.accentPreset = "violet"
        settings.customAccentHex = "#123ABC"
        settings.companionFollowsAccent = false
        settings.customCompanionHex = "#CDEF12"
        #expect(defaults.string(forKey: "appearance.accentPreset") == "violet")
        #expect(defaults.string(forKey: "appearance.customCompanionHex") == "#CDEF12")
    }

    @Test @MainActor func savedPresetAndCustomColoursArePreservedWhenSettingsLoad() {
        let key = "clicky-theme-tests-legacy-\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: key)!
        defer { defaults.removePersistentDomain(forName: key) }
        defaults.set("coral", forKey: "appearance.accentPreset")
        defaults.set("#123ABC", forKey: "appearance.customAccentHex")
        defaults.set(false, forKey: "appearance.companionFollowsAccent")
        defaults.set("#CDEF12", forKey: "appearance.customCompanionHex")

        let settings = DictationSettings(defaults: defaults)

        #expect(settings.accentPreset == "coral")
        #expect(ClickyThemePalette.resolve(preset: settings.accentPreset, customHex: settings.customAccentHex, dark: false)
            == ClickyThemePalette.resolve(preset: "coral", customHex: "#123ABC", dark: false))
        #expect(settings.customAccentHex == "#123ABC")
        #expect(!settings.companionFollowsAccent)
        #expect(settings.customCompanionHex == "#CDEF12")
        #expect(defaults.string(forKey: "appearance.accentPreset") == "coral")
    }

    @Test @MainActor func resetColoursSelectsNavyAndFollowModeWithoutChangingAppearanceOrCustomValues() {
        let key = "clicky-theme-tests-reset-\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: key)!
        defer { defaults.removePersistentDomain(forName: key) }
        let settings = DictationSettings(defaults: defaults)
        settings.appearance = .dark
        settings.accentPreset = "custom"
        settings.customAccentHex = "#123ABC"
        settings.companionFollowsAccent = false
        settings.customCompanionHex = "#CDEF12"

        settings.resetColours()

        #expect(settings.accentPreset == "navy")
        #expect(settings.companionFollowsAccent)
        #expect(settings.customAccentHex == "#123ABC")
        #expect(settings.customCompanionHex == "#CDEF12")
        #expect(settings.appearance == .dark)
    }
}
