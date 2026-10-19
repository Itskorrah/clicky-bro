using OpenClicky.Core.Configuration;
using OpenClicky.Core.Dictation;

namespace OpenClicky.Core.Tests.Dictation;

public sealed class ClickyAccentPaletteTests
{
    [Fact]
    public void AzurePresetMatchesManifestInBothAppearances()
    {
        Assert.Equal("#2563EB", ClickyAccentPalette.Resolve("azure", "#FFFFFF", dark: false));
        Assert.Equal("#60A5FA", ClickyAccentPalette.Resolve("azure", "#FFFFFF", dark: true));
        Assert.Equal("#2563EB", ClickyAccentPalette.ResolveCompanion(
            "azure", "#FFFFFF", followAccent: true, customCompanionHex: "#000000", dark: false));
        Assert.Equal("#60A5FA", ClickyAccentPalette.ResolveCompanion(
            "azure", "#FFFFFF", followAccent: true, customCompanionHex: "#000000", dark: true));
        Assert.True(ClickyAccentPalette.Contrast("#2563EB", "#F6F8FA") >= 4.5);
        Assert.True(ClickyAccentPalette.Contrast("#60A5FA", "#21262D") >= 4.5);
    }

    [Fact]
    public void NavySlateIsTheNewInstallDefaultAndMatchesBothAppearanceSurfaces()
    {
        Assert.Contains(ClickyAccentPalette.Presets, item => item.Id == "coral");
        Assert.Equal("navy", ClickyAccentPalette.DefaultPresetId);
        Assert.Equal("#2B547B", ClickyAccentPalette.Resolve("navy", "#FFFFFF", dark: false));
        Assert.Equal("#80A9D4", ClickyAccentPalette.Resolve("navy", "#FFFFFF", dark: true));
        Assert.NotEqual(ClickyAccentPalette.Resolve("navy", "#FFFFFF", dark: false),
                        ClickyAccentPalette.Resolve("coral", "#FFFFFF", dark: false));
        Assert.True(ClickyAccentPalette.Contrast("#2B547B", "#F6F8FA") >= 4.5);
        Assert.True(ClickyAccentPalette.Contrast("#80A9D4", "#21262D") >= 4.5);
    }

    [Fact]
    public void EveryPresetUsesReadableColoursOnLightAndDarkSurfaces()
    {
        foreach (var preset in ClickyAccentPalette.Presets)
        foreach (var dark in new[] { false, true })
        {
            var hex = ClickyAccentPalette.Resolve(preset.Id, "#FFFFFF", dark);
            Assert.True(ClickyAccentPalette.Contrast(hex, dark ? "#21262D" : "#F6F8FA") >= 4.5,
                        $"Invalid contrast for {preset.Id} ({(dark ? "dark" : "light")}): {hex}");
            Assert.True(ClickyAccentPalette.Contrast(ClickyAccentPalette.TextOnAccent(hex), hex) >= 4.5);
        }
    }

    [Fact]
    public void InvalidCustomHexIsIgnoredAndUnknownPresetFallsBackToNavy()
    {
        Assert.Equal("#ABCDEF", ClickyAccentPalette.NormalizeHex(" abcdef "));
        Assert.Null(ClickyAccentPalette.NormalizeHex("#12345"));
        Assert.Null(ClickyAccentPalette.NormalizeHex("##ABCDEF"));
        Assert.Null(ClickyAccentPalette.NormalizeHex("12345678"));
        Assert.Equal(ClickyAccentPalette.Resolve("navy", "", false),
                     ClickyAccentPalette.Resolve("unsupported", "", false));
        foreach (var dark in new[] { false, true })
        {
            Assert.Equal(dark ? "#7590A9" : ClickyAccentPalette.DefaultAccentHex,
                         ClickyAccentPalette.ResolveCompanion("navy", "", followAccent: false,
                                                               customCompanionHex: "invalid", dark));
        }
    }

    [Fact]
    public void PreferencesPersistWithoutOverwritingExistingAppearance()
    {
        var defaults = Preferences.InMemory();
        var settings = new DictationSettings(defaults);
        Assert.Equal(DictationAppearance.System, settings.Appearance);
        Assert.Equal("navy", settings.AccentPreset);
        Assert.Equal("#2B547B", settings.CustomAccentHex);
        Assert.True(settings.CompanionFollowsAccent);
        Assert.Equal("#2B547B", settings.CustomCompanionHex);
        settings.AccentPreset = "violet";
        settings.CustomAccentHex = "#112233";
        settings.CompanionFollowsAccent = false;
        settings.CustomCompanionHex = "#ABCDEF";
        settings.CustomCompanionHex = "invalid";
        var reloaded = new DictationSettings(defaults);
        Assert.Equal("violet", reloaded.AccentPreset);
        Assert.Equal("#112233", reloaded.CustomAccentHex);
        Assert.False(reloaded.CompanionFollowsAccent);
        Assert.Equal("#ABCDEF", reloaded.CustomCompanionHex);
        Assert.Equal(DictationAppearance.System, reloaded.Appearance);
    }

    [Fact]
    public void ExistingPresetAndCustomColoursArePreservedWhenSettingsLoad()
    {
        var defaults = Preferences.InMemory();
        defaults.Set("appearance.accentPreset", "coral");
        defaults.Set("appearance.customAccentHex", "#123ABC");
        defaults.Set("appearance.companionFollowsAccent", false);
        defaults.Set("appearance.customCompanionHex", "#CDEF12");

        var settings = new DictationSettings(defaults);

        Assert.Equal("coral", settings.AccentPreset);
        Assert.Equal(ClickyAccentPalette.Resolve("coral", "#123ABC", dark: false),
                     ClickyAccentPalette.Resolve(settings.AccentPreset, settings.CustomAccentHex, dark: false));
        Assert.Equal("#123ABC", settings.CustomAccentHex);
        Assert.False(settings.CompanionFollowsAccent);
        Assert.Equal("#CDEF12", settings.CustomCompanionHex);
        Assert.Equal("coral", defaults.GetString("appearance.accentPreset"));
    }

    [Fact]
    public void ResetColoursSelectsNavyAndFollowModeWithoutChangingAppearanceOrCustomValues()
    {
        var settings = new DictationSettings(Preferences.InMemory())
        {
            Appearance = DictationAppearance.Dark,
            AccentPreset = "custom",
            CustomAccentHex = "#123ABC",
            CompanionFollowsAccent = false,
            CustomCompanionHex = "#CDEF12",
        };

        settings.ResetColours();

        Assert.Equal("navy", settings.AccentPreset);
        Assert.True(settings.CompanionFollowsAccent);
        Assert.Equal("#123ABC", settings.CustomAccentHex);
        Assert.Equal("#CDEF12", settings.CustomCompanionHex);
        Assert.Equal(DictationAppearance.Dark, settings.Appearance);
    }
}
