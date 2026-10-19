using System.Globalization;

namespace OpenClicky.Core.Dictation;

/// <summary>Semantic accent colours shared by the settings window and companion.
/// Pure and dependency-free so arbitrary user input cannot crash native drawing.</summary>
public static class ClickyAccentPalette
{
    public static IReadOnlyList<(string Id, string Name)> Presets { get; } =
    [
        ("coral", "Classic Coral"), ("azure", "Azure Blue"), ("emerald", "Emerald"),
        ("violet", "Violet"), ("graphite", "Graphite"), ("custom", "Custom")
    ];

    public static string? NormalizeHex(string? value)
    {
        var raw = value?.Trim();
        if (raw is not null && raw.StartsWith('#')) raw = raw[1..];
        if (raw?.Length != 6 || !raw.All(Uri.IsHexDigit)) return null;
        return "#" + raw.ToUpperInvariant();
    }

    public static string Resolve(string? preset, string? customHex, bool dark)
    {
        var baseColour = (preset ?? "coral").ToLowerInvariant() switch
        {
            "azure" => dark ? "#60A5FA" : "#2563EB",
            "emerald" => dark ? "#34D399" : "#047857",
            "violet" => dark ? "#A78BFA" : "#6D28D9",
            "graphite" => dark ? "#CBD5E1" : "#475569",
            "custom" => NormalizeHex(customHex) ?? (dark ? "#E8653F" : "#D24E2A"),
            _ => dark ? "#E8653F" : "#D24E2A",
        };
        // Accent labels on plain surfaces need 4.5:1 contrast. Preserve hue while
        // moving custom and preset colours towards a suitable luminance.
        return EnsureContrast(baseColour, dark ? "#202329" : "#FFFFFF", dark);
    }

    public static string ResolveCompanion(string preset, string? customAccentHex,
                                           bool followAccent, string? customCompanionHex, bool dark) =>
        followAccent ? Resolve(preset, customAccentHex, dark)
                     : EnsureContrast(NormalizeHex(customCompanionHex) ?? "#E8653F",
                                      dark ? "#202329" : "#FFFFFF", dark);

    /// <summary>Choose readable bubble copy regardless of a user-chosen background tint.</summary>
    public static string TextOnAccent(string accent) =>
        Contrast("#FFFFFF", accent) >= Contrast("#0F172A", accent) ? "#FFFFFF" : "#0F172A";

    public static double Contrast(string first, string second)
    {
        var a = Luminance(first);
        var b = Luminance(second);
        return (Math.Max(a, b) + 0.05) / (Math.Min(a, b) + 0.05);
    }

    private static double Luminance(string hex)
    {
        double Channel(int offset)
        {
            var channel = byte.Parse(hex.AsSpan(offset, 2), NumberStyles.HexNumber,
                                      CultureInfo.InvariantCulture) / 255.0;
            return channel <= 0.04045 ? channel / 12.92 : Math.Pow((channel + 0.055) / 1.055, 2.4);
        }
        return 0.2126 * Channel(1) + 0.7152 * Channel(3) + 0.0722 * Channel(5);
    }

    private static string EnsureContrast(string colour, string background, bool dark)
    {
        if (Contrast(colour, background) >= 4.5) return colour;
        var red = Convert.ToInt32(colour.Substring(1, 2), 16);
        var green = Convert.ToInt32(colour.Substring(3, 2), 16);
        var blue = Convert.ToInt32(colour.Substring(5, 2), 16);
        for (var i = 1; i <= 100; i++)
        {
            var fraction = i / 100.0;
            var target = dark ? 255 : 0;
            var candidate = $"#{(int)Math.Round(red + (target - red) * fraction):X2}{(int)Math.Round(green + (target - green) * fraction):X2}{(int)Math.Round(blue + (target - blue) * fraction):X2}";
            if (Contrast(candidate, background) >= 4.5) return candidate;
        }
        return dark ? "#FFFFFF" : "#000000";
    }
}
