// Ports Dictation/UI/SettingsGeneralPage.swift (and the update rows of SettingsAboutPage.swift):
// where you are, how OpenClicky looks and starts, and updates. The region, appearance, where the
// island lives, the tray icon (always on while the island is hidden), open at sign-in (the HKCU Run
// value, ILoginItem), the two tours, reduce motion, and software updates (IAppUpdater, Velopack).

using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using OpenClicky.Core.Configuration;
using OpenClicky.Core.Dictation;
using OpenClicky.Core.Pointing;
using OpenClicky.Core.Settings;
using OpenClicky.Windows.Theme;

namespace OpenClicky.Windows.AppWindow;

internal sealed partial class SettingsRowFactory
{
    public static string HudPlacementTitle(HUDPlacement placement) => placement switch
    {
        HUDPlacement.Notch => "Top of the screen",
        HUDPlacement.Left => "Left edge",
        HUDPlacement.Right => "Right edge",
        _ => "Hidden",
    };

    public static string HudPlacementDetail(HUDPlacement placement) => placement switch
    {
        HUDPlacement.Notch => "Hangs from the top of the screen. Hover it to open.",
        HUDPlacement.Left => "A drawer on the left edge of every screen. Hover the handle to open.",
        HUDPlacement.Right => "A drawer on the right edge of every screen. Hover the handle to open.",
        _ => "Nothing on screen until you use a shortcut. The tray icon opens the panel.",
    };

    private UIElement? GeneralRow(SettingsItem item, string query)
    {
        var companion = services.Companion;
        switch (item.Id)
        {
            case "general.region":
                return LiveSettingsCard(() => Ui.Row(item.Title, item.Detail, query,
                    Ui.Picker(Enum.GetValues<AppRegion>().Select(region => (region, region.Title())), Settings.Region, region => Settings.Region = region, 180)));
            case "general.appearance":
                return LiveSettingsCard(() => AppearanceRow(item, query));
            case "general.colourScheme":
                return LiveSettingsCard(() => ColourSchemeRow(item, query));
            case "general.hudPlacement":
                return new LiveContent(() => Ui.Card(Ui.Row(item.Title, HudPlacementDetail(companion.HudPlacement), query,
                    Ui.Picker(HUDPlacements.AllCases.Select(placement => (placement, HudPlacementTitle(placement))), companion.HudPlacement,
                        companion.SetHudPlacement, 180))),
                    Changes.Of(companion, nameof(ICompanionSettings.HudPlacement)));
            case "general.trayIcon":
                return new LiveContent(() =>
                {
                    // Forced on while the island is hidden: the tray icon is then the only way into the panel.
                    var isForcedOn = companion.HudPlacement == HUDPlacement.Hidden;
                    var detail = isForcedOn ? "Always on while clicky-bro is hidden, so you can still reach it." : item.Detail;
                    return Ui.Card(Ui.Row(item.Title, detail, query,
                        Ui.Toggle(companion.IsTrayIconVisible || isForcedOn, companion.SetTrayIconVisible, isEnabled: !isForcedOn)));
                }, Changes.Of(companion, nameof(ICompanionSettings.IsTrayIconVisible), nameof(ICompanionSettings.HudPlacement)));
            case "general.openAtLogin":
                return LoginItemRow(item, query);
            case "general.walkthrough":
                return Ui.Card(Ui.Row(item.Title, item.Detail, query, Ui.Button("Replay…", companion.ReplayWelcomeTour)));
            case "general.settingsTour":
                return Ui.Card(Ui.Row(item.Title, item.Detail, query, Ui.Button("Play", actions.StartSettingsTour)));
            case "general.reduceMotion":
                return SettingsToggleRow(item.Title, item.Detail, query, () => Settings.ReduceAnimation, isOn => Settings.ReduceAnimation = isOn, nameof(DictationSettings.ReduceAnimation));
            case "about.autoUpdate":
                return new LiveContent(() =>
                {
                    var updater = services.Updater;
                    var description = updater.LastCheckDescription;
                    var detail = updater.IsConfigured
                        ? (description.Length > 0 ? char.ToUpper(description[0]) + description[1..] + "." : item.Detail)
                        : "This build has no update feed (a development build).";
                    return Ui.Card(Ui.Row(item.Title, detail, query,
                        Ui.Toggle(updater.AutomaticallyChecks, isOn => updater.AutomaticallyChecks = isOn, isEnabled: updater.IsConfigured)));
                }, Changes.Of(services.Updater));
            case "about.checkNow":
                return new LiveContent(() => Ui.Card(Ui.Row(item.Title, null, query,
                    Ui.Button("Check Now", services.Updater.CheckNow, isEnabled: services.Updater.IsConfigured))), Changes.Of(services.Updater));
            default:
                return null;
        }
    }

    private UIElement LoginItemRow(SettingsItem item, string query)
    {
        LiveContent? row = null;
        row = new LiveContent(() => Ui.Card(Ui.Row(item.Title, item.Detail, query, Ui.Toggle(services.LoginItem.IsEnabled, isOn =>
        {
            var nowEnabled = services.LoginItem.SetEnabled(isOn);
            if (nowEnabled != isOn) AppLog.Write($"login item: couldn't switch {(isOn ? "on" : "off")}");
            row?.Rebuild();
        }))), Changes.Of(Settings, nameof(DictationSettings.DictationKey)));
        return row;
    }

    /// <summary>Light, Dark and Auto as three tiles, the chosen one ringed in the accent.</summary>
    private Grid AppearanceRow(SettingsItem item, string query)
    {
        var tiles = new StackPanel { Orientation = Orientation.Horizontal };
        foreach (var appearance in new[] { DictationAppearance.Light, DictationAppearance.Dark, DictationAppearance.System })
        {
            tiles.Children.Add(AppearanceTile(appearance, Settings.Appearance == appearance, () => Settings.Appearance = appearance));
        }
        return Ui.Row(item.Title, item.Detail, query, tiles);
    }

    /// <summary>Preserves the existing settings row and native WPF-UI controls.</summary>
    private Grid ColourSchemeRow(SettingsItem item, string query)
    {
        var controls = new StackPanel { Width = 240 };
        var preset = Ui.Picker(ClickyAccentPalette.Presets.Select(choice => (choice.Id, choice.Name)),
                               Settings.AccentPreset, id => Settings.AccentPreset = id, minWidth: 190);
        Ui.AutomationProperties(preset, "App accent colour");
        controls.Children.Add(preset);

        if (Settings.AccentPreset == "custom")
        {
            var editor = HexColourEditor("Custom accent", Settings.CustomAccentHex, value => Settings.CustomAccentHex = value);
            editor.Margin = new Thickness(0, 7, 0, 0);
            controls.Children.Add(editor);
        }

        var followRow = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 9, 0, 0) };
        var followLabel = Ui.Text("Companion follows accent", SettingsLook.CaptionSize, SettingsLook.TextPrimary, wrap: false);
        followLabel.VerticalAlignment = VerticalAlignment.Center;
        followRow.Children.Add(followLabel);
        var followToggle = Ui.Toggle(Settings.CompanionFollowsAccent, value => Settings.CompanionFollowsAccent = value);
        followToggle.Margin = new Thickness(10, 0, 0, 0);
        Ui.AutomationProperties(followToggle, "Companion follows accent");
        followRow.Children.Add(followToggle);
        controls.Children.Add(followRow);

        if (!Settings.CompanionFollowsAccent)
        {
            var editor = HexColourEditor("Companion colour", Settings.CustomCompanionHex,
                value => Settings.CustomCompanionHex = value);
            editor.Margin = new Thickness(0, 7, 0, 0);
            controls.Children.Add(editor);
        }

        var reset = Ui.LinkButton("Reset colours", Settings.ResetColours);
        reset.Margin = new Thickness(0, 9, 0, 0);
        Ui.AutomationProperties(reset, "Reset colours to Navy Slate");
        controls.Children.Add(reset);
        return Ui.Row(item.Title, item.Detail, query, controls);
    }

    /// <summary>A genuine Windows colour picker plus validated hex input. Invalid text never reaches settings.</summary>
    private static StackPanel HexColourEditor(string label, string initialHex, Action<string> change)
    {
        var group = new StackPanel();
        var row = new StackPanel { Orientation = Orientation.Horizontal };
        var input = new TextBox { Text = initialHex, Width = 108, MaxLength = 7, VerticalContentAlignment = VerticalAlignment.Center };
        Ui.AutomationProperties(input, label + " RGB hex", "Enter #RRGGBB");
        row.Children.Add(input);
        var error = Ui.Text("", SettingsLook.MicroSize, SettingsLook.TextSecondary);
        void Apply()
        {
            var normal = ClickyAccentPalette.NormalizeHex(input.Text);
            if (normal is null)
            {
                error.Text = "Enter a six-digit colour, e.g. #2B547B.";
                return;
            }
            error.Text = "";
            input.Text = normal;
            change(normal);
        }
        var apply = Ui.Button("Apply", Apply);
        apply.Margin = new Thickness(6, 0, 0, 0);
        row.Children.Add(apply);
        var choose = Ui.Button("Choose…", () =>
        {
            using var picker = new System.Windows.Forms.ColorDialog
            {
                FullOpen = true, AnyColor = true,
                Color = System.Drawing.ColorTranslator.FromHtml(
                    ClickyAccentPalette.NormalizeHex(input.Text) ?? initialHex),
            };
            if (picker.ShowDialog() != System.Windows.Forms.DialogResult.OK) return;
            input.Text = $"#{picker.Color.R:X2}{picker.Color.G:X2}{picker.Color.B:X2}";
            Apply();
        });
        choose.Margin = new Thickness(6, 0, 0, 0);
        row.Children.Add(choose);
        input.KeyDown += (_, args) =>
        {
            if (args.Key == Key.Enter) { Apply(); args.Handled = true; }
        };
        group.Children.Add(row);
        group.Children.Add(error);
        return group;
    }

    private static Button AppearanceTile(DictationAppearance appearance, bool isSelected, Action choose)
    {
        var label = appearance switch { DictationAppearance.Light => "Light", DictationAppearance.Dark => "Dark", _ => "Auto" };
        var light = DS.Brush(DS.Colors.PrimerLight.Canvas);
        var dark = DS.Brush(DS.Colors.PrimerDark.Canvas);
        var lightSurface = DS.Brush(DS.Colors.PrimerLight.Surface);
        var darkSurface = DS.Brush(DS.Colors.PrimerDark.Surface);
        var picture = new Grid { Width = 68, Height = 46, ClipToBounds = true };
        picture.Children.Add(new Border { Background = appearance == DictationAppearance.Dark ? dark : light, CornerRadius = new CornerRadius(7) });
        if (appearance == DictationAppearance.System)
        {
            var darkHalf = new System.Windows.Shapes.Path
            {
                Data = Geometry.Parse("M 68,0 L 68,46 L 0,46 Z"),
                Fill = dark,
                Clip = new RectangleGeometry(new Rect(0, 0, 68, 46), 7, 7),
            };
            picture.Children.Add(darkHalf);
        }
        picture.Children.Add(new Border
        {
            Width = 48, Height = 26, CornerRadius = new CornerRadius(4),
            Background = appearance == DictationAppearance.Dark ? darkSurface : lightSurface,
            BorderBrush = DS.Brush(appearance == DictationAppearance.Dark ? DS.Colors.PrimerDark.Border : DS.Colors.PrimerLight.Border),
            BorderThickness = new Thickness(0.5),
        });
        var capsule = new Border { Width = 28, Height = 18, CornerRadius = new CornerRadius(9), HorizontalAlignment = HorizontalAlignment.Center, VerticalAlignment = VerticalAlignment.Center };
        capsule.SetResourceReference(Border.BackgroundProperty, SettingsLook.Accent);
        picture.Children.Add(capsule);
        var ring = new Border { CornerRadius = new CornerRadius(7), BorderThickness = new Thickness(isSelected ? 2 : 1) };
        ring.SetResourceReference(Border.BorderBrushProperty, isSelected ? SettingsLook.Accent : SettingsLook.ControlStroke);
        picture.Children.Add(ring);
        var caption = Ui.Text(label, SettingsLook.CaptionSize, isSelected ? SettingsLook.TextPrimary : SettingsLook.TextSecondary,
            isSelected ? FontWeights.SemiBold : FontWeights.Normal, wrap: false);
        caption.HorizontalAlignment = HorizontalAlignment.Center;
        caption.Margin = new Thickness(0, 6, 0, 0);
        var stack = new StackPanel();
        stack.Children.Add(picture);
        stack.Children.Add(caption);
        var button = new Button { Content = stack, Template = Ui.TransparentButtonTemplate(), Cursor = Cursors.Hand, Margin = new Thickness(6, 0, 6, 0) };
        Ui.AutomationProperties(button, isSelected ? $"{label}, selected" : label);
        button.Click += (_, _) => choose();
        return button;
    }
}
