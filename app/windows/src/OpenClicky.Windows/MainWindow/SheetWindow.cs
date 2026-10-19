// The Mac's sheets (AccountSheet, the take, term, snippet, style and app-picker sheets, the
// confirmation dialogs) as small Fluent dialog windows owned by the main window, each with the
// theme installed and the Cancel (Esc) / default (Enter) buttons at its foot. Also the mark
// (OpenClickyMark.swift), drawn for About, the generated tray icon and the window icon.

using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using OpenClicky.Core.Dictation;
using WpfUi = Wpf.Ui.Controls;

namespace OpenClicky.Windows.AppWindow;

internal class SheetWindow : WpfUi.FluentWindow
{
    private readonly DockPanel root = new() { LastChildFill = true };
    private readonly StackPanel footerLeft = new() { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Left };
    private readonly StackPanel footerRight = new() { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right };
    private readonly Border footerBar;

    public SheetWindow(Window? owner, DictationSettings settings, string title, double width)
    {
        Owner = owner;
        Title = title;
        Width = width;
        SizeToContent = SizeToContent.Height;
        MaxHeight = 760;
        ResizeMode = ResizeMode.NoResize;
        ShowInTaskbar = owner is null;
        WindowStartupLocation = owner is null ? WindowStartupLocation.CenterScreen : WindowStartupLocation.CenterOwner;
        ExtendsContentIntoTitleBar = true;
        WindowBackdropType = WpfUi.WindowBackdropType.Mica;
        WindowCornerPreference = WpfUi.WindowCornerPreference.Round;
        MainWindowTheme.Install(this, settings);

        var titleBar = new WpfUi.TitleBar { Title = title, ShowMaximize = false, ShowMinimize = false, CanMaximize = false };
        DockPanel.SetDock(titleBar, Dock.Top);
        root.Children.Add(titleBar);
        var footer = new Grid();
        footer.Children.Add(footerLeft);
        footer.Children.Add(footerRight);
        footerBar = new Border { Padding = new Thickness(24, 14, 24, 18), Child = footer, BorderThickness = new Thickness(0, 1, 0, 0) };
        footerBar.SetResourceReference(Border.BorderBrushProperty, SettingsLook.Divider);
        footerBar.SetResourceReference(Border.BackgroundProperty, "SolidBackgroundFillColorBaseBrush");
        DockPanel.SetDock(footerBar, Dock.Bottom);
        root.Children.Add(footerBar);
        Content = root;
        PreviewKeyDown += (_, arguments) =>
        {
            if (arguments.Key == Key.Escape) Close();
        };
    }

    /// <summary>The sheet's body, scrolled when it is taller than the screen allows.</summary>
    public void SetBody(UIElement body, Thickness? padding = null)
    {
        var scroller = new ScrollViewer
        {
            Content = body,
            Padding = padding ?? new Thickness(24, 8, 24, 16),
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
        };
        if (root.Children.Count > 2) root.Children.RemoveAt(2);
        root.Children.Add(scroller);
    }

    public void HideFooter() => footerBar.Visibility = Visibility.Collapsed;

    /// <summary>A footer button; the default one answers Enter, the cancel one Esc.</summary>
    public WpfUi.Button AddFooterButton(string title, Action onClick, bool isDefault = false, bool isCancel = false,
        WpfUi.ControlAppearance? appearance = null, bool alignLeft = false)
    {
        var button = Ui.Button(title, onClick, appearance ?? (isDefault ? WpfUi.ControlAppearance.Primary : WpfUi.ControlAppearance.Secondary));
        button.IsDefault = isDefault;
        button.IsCancel = isCancel;
        button.MinWidth = 80;
        if (alignLeft)
        {
            button.Margin = new Thickness(0, 0, 8, 0);
            footerLeft.Children.Add(button);
        }
        else
        {
            button.Margin = new Thickness(8, 0, 0, 0);
            footerRight.Children.Add(button);
        }
        return button;
    }

    /// <summary>A yes/no question, as the Mac's confirmationDialog. Returns whether the destructive action was chosen.</summary>
    public static bool Confirm(Window? owner, DictationSettings settings, string title, string message, string actionTitle)
    {
        var confirmed = false;
        var sheet = new SheetWindow(owner, settings, "clicky-bro", 420);
        var body = Ui.VStack(8,
            Ui.Text(title, 16, SettingsLook.TextPrimary, FontWeights.SemiBold),
            Ui.Text(message, 13, SettingsLook.TextSecondary));
        sheet.SetBody(body, new Thickness(24, 4, 24, 18));
        sheet.AddFooterButton("Cancel", sheet.Close, isCancel: true);
        sheet.AddFooterButton(actionTitle, () => { confirmed = true; sheet.Close(); }, isDefault: true, appearance: WpfUi.ControlAppearance.Danger);
        sheet.ShowDialog();
        return confirmed;
    }
}

/// <summary>The Clicky Bro assistant face and its four-point spark.</summary>
public static class OpenClickyMarkDrawing
{
    private static readonly SolidColorBrush InkBrush = Brush(0x13, 0x23, 0x3B);
    private static readonly SolidColorBrush CobaltBrush = Brush(0x2F, 0x81, 0xF7);
    private static readonly SolidColorBrush PaleCyanBrush = Brush(0xA5, 0xD6, 0xFF);
    private static readonly SolidColorBrush PaperBrush = Brush(0xF0, 0xF6, 0xFC);

    private static SolidColorBrush Brush(byte red, byte green, byte blue)
    {
        var brush = new SolidColorBrush(Color.FromRgb(red, green, blue));
        brush.Freeze();
        return brush;
    }

    private static Rect UnitRect(double left, double top, double side, double x0, double y0, double x1, double y1) =>
        new(left + x0 * side, top + y0 * side, (x1 - x0) * side, (y1 - y0) * side);

    private static Geometry Rounded(double left, double top, double side,
        double x0, double y0, double x1, double y1, double radius)
    {
        var geometry = new RectangleGeometry(UnitRect(left, top, side, x0, y0, x1, y1), radius * side, radius * side);
        geometry.Freeze();
        return geometry;
    }

    private static Geometry BodyGeometry(double left, double top, double side)
    {
        var group = new GeometryGroup { FillRule = FillRule.Nonzero };
        group.Children.Add(Rounded(left, top, side, 0.31, 0.66, 0.445, 0.79, 0.055));
        group.Children.Add(Rounded(left, top, side, 0.555, 0.66, 0.69, 0.79, 0.055));
        group.Children.Add(Rounded(left, top, side, 0.21, 0.27, 0.79, 0.73, 0.15));
        group.Freeze();
        return group;
    }

    private static Geometry SparkGeometry(double left, double top, double side)
    {
        var cx = left + 0.755 * side;
        var cy = top + 0.30 * side;
        var radius = 0.13 * side;
        var shoulder = 0.033 * side;
        var points = new[]
        {
            new Point(cx, cy - radius),
            new Point(cx + shoulder, cy - shoulder),
            new Point(cx + radius, cy),
            new Point(cx + shoulder, cy + shoulder),
            new Point(cx, cy + radius),
            new Point(cx - shoulder, cy + shoulder),
            new Point(cx - radius, cy),
            new Point(cx - shoulder, cy - shoulder),
        };
        var path = new StreamGeometry();
        using (var context = path.Open())
        {
            context.BeginFigure(points[0], isFilled: true, isClosed: true);
            for (var index = 1; index < points.Length; index++)
                context.LineTo(points[index], isStroked: true, isSmoothJoin: false);
        }
        path.Freeze();
        return path;
    }

    private static Geometry FaceGeometry(double left, double top, double side) =>
        Rounded(left, top, side, 0.285, 0.36, 0.715, 0.63, 0.105);

    private static Geometry EyesGeometry(double left, double top, double side)
    {
        var group = new GeometryGroup();
        group.Children.Add(new EllipseGeometry(UnitRect(left, top, side, 0.385, 0.455, 0.455, 0.545)));
        group.Children.Add(new EllipseGeometry(UnitRect(left, top, side, 0.545, 0.455, 0.615, 0.545)));
        group.Freeze();
        return group;
    }

    /// <summary>The monochrome mark silhouette in a square at (<paramref name="left"/>, <paramref name="top"/>).</summary>
    public static Geometry Geometry(double left, double top, double side)
    {
        var group = new GeometryGroup { FillRule = FillRule.Nonzero };
        group.Children.Add(BodyGeometry(left, top, side));
        group.Children.Add(SparkGeometry(left, top, side));
        group.Freeze();
        return group;
    }

    /// <summary>The flat navy app tile with its cobalt assistant face and pale-cyan spark.</summary>
    public static DrawingImage AppIconImage()
    {
        var group = new DrawingGroup();
        var tile = new RectangleGeometry(new Rect(0, 0, 64, 64), 14, 14);
        tile.Freeze();
        group.Children.Add(new GeometryDrawing(InkBrush, null, tile));
        group.Children.Add(new GeometryDrawing(CobaltBrush, null, BodyGeometry(0, 0, 64)));
        group.Children.Add(new GeometryDrawing(PaperBrush, null, FaceGeometry(0, 0, 64)));
        group.Children.Add(new GeometryDrawing(InkBrush, null, EyesGeometry(0, 0, 64)));
        group.Children.Add(new GeometryDrawing(PaleCyanBrush, null, SparkGeometry(0, 0, 64)));
        var image = new DrawingImage(group);
        image.Freeze();
        return image;
    }

    /// <summary>The app icon rendered to a bitmap of <paramref name="pixels"/> square.</summary>
    public static BitmapSource AppIconBitmap(int pixels)
    {
        var visual = new DrawingVisual();
        using (var context = visual.RenderOpen())
        {
            context.DrawImage(AppIconImage(), new Rect(0, 0, pixels, pixels));
        }
        var bitmap = new RenderTargetBitmap(pixels, pixels, 96, 96, PixelFormats.Pbgra32);
        bitmap.Render(visual);
        bitmap.Freeze();
        return bitmap;
    }
}
