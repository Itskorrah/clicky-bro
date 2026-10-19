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
        Assert.True(ClickyAccentPalette.Contrast("#2563EB", "#FFFFFF") >= 4.5);
        Assert.True(ClickyAccentPalette.Contrast("#60A5FA", "#202329") >= 4.5);
    }

    [Fact]
    public void EveryPresetUsesReadableColoursOnLightAndDarkSurfaces()
    {
        foreach (var preset in ClickyAccentPalette.Presets)
        foreach (var dark in new[] { false, true })
        {
            var hex = ClickyAccentPalette.Resolve(preset.Id, "#FFFFFF", dark);
            Assert.True(ClickyAccentPalette.Contrast(hex, dark ? "#202329" : "#FFFFFF") >= 4.5,
                        $"Invalid contrast for {preset.Id} ({(dark ? "dark" : "light")}): {hex}");
            Assert.True(ClickyAccentPalette.Contrast(ClickyAccentPalette.TextOnAccent(hex), hex) >= 4.5);
        }
    }

    [Fact]
    public void InvalidCustomHexIsIgnoredAndUnknownPresetFallsBackToCoral()
    {
        Assert.Equal("#ABCDEF", ClickyAccentPalette.NormalizeHex(" abcdef "));
        Assert.Null(ClickyAccentPalette.NormalizeHex("#12345"));
        Assert.Null(ClickyAccentPalette.NormalizeHex("##ABCDEF"));
        Assert.Null(ClickyAccentPalette.NormalizeHex("12345678"));
        Assert.Equal(ClickyAccentPalette.Resolve("coral", "", false),
                     ClickyAccentPalette.Resolve("unsupported", "", false));
    }

    [Fact]
    public void PreferencesPersistWithoutOverwritingExistingAppearance()
    {
        var defaults = Preferences.InMemory();
        var settings = new DictationSettings(defaults);
        Assert.Equal(DictationAppearance.System, settings.Appearance);
        Assert.Equal("coral", settings.AccentPreset);
        Assert.True(settings.CompanionFollowsAccent);
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
}
