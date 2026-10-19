// Ports MenuBarPanelManager.swift: the tray icon (the Mac's NSStatusItem) and its plain menu, for
// either click: what OpenClicky is doing and the keys to remember, agent mode, docking the pointer,
// the window, the island, settings, the welcome tour, and quit. Each item is raised as an event the
// composition root wires (Wired in AppComposition.WireTray: CompanionManager.setAgentModeEnabled, setCursorDocked,
// showDictationWindow(section: .words), notchHUDManager.openPanel, showSettings, firstRunTour.replay,
// quitWithFarewell). The icon is Assets\OpenClicky.ico when the app ships one, else the mark drawn here.

using System.IO;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using OpenClicky.Core.Configuration;

namespace OpenClicky.Windows.Tray;

/// <summary>What the menu shows, read each time it opens.</summary>
public sealed record TrayMenuState(
    string StatusText,
    bool IsAgentModeEnabled,
    bool IsCursorDocked,
    bool IslandIsSideDrawer,
    string DictationKeyLabel)
{
    /// <summary>"Ready", or what OpenClicky is busy with (MenuBarPanelManager.statusText).</summary>
    public static string StatusTextFor(string voiceState, bool agentIsWorking) => voiceState switch
    {
        "listening" => "Listening",
        "processing" => "Thinking",
        "responding" => "Speaking",
        _ => agentIsWorking ? "Agent working" : "Ready",
    };
}

public sealed class TrayIcon : IDisposable
{
    private readonly NotifyIcon notifyIcon;
    private readonly Func<TrayMenuState> readState;
    private readonly Icon icon;

    public event Action? AgentModeToggled;
    public event Action? DockToggled;
    public event Action? OpenWindowRequested;
    public event Action? OpenIslandRequested;
    public event Action? SettingsRequested;
    public event Action? ReplayWelcomeRequested;
    public event Action? QuitRequested;

    public TrayIcon(Func<TrayMenuState> readState)
    {
        this.readState = readState;
        icon = LoadIcon();
        notifyIcon = new NotifyIcon { Icon = icon, Text = "Clicky Bro", Visible = false };
        notifyIcon.ContextMenuStrip = new ContextMenuStrip { ShowCheckMargin = true, ShowImageMargin = false };
        notifyIcon.ContextMenuStrip.Opening += (_, _) => BuildMenu(notifyIcon.ContextMenuStrip);
        // Either click opens the menu, as on the Mac.
        notifyIcon.MouseUp += (_, arguments) =>
        {
            if (arguments.Button != MouseButtons.Left) return;
            ShowContextMenuAtCursor();
        };
    }

    /// <summary>Shown or hidden (Settings › General › Show in the tray; always shown while the island is hidden).</summary>
    public bool IsVisible
    {
        get => notifyIcon.Visible;
        set => notifyIcon.Visible = value;
    }

    private void ShowContextMenuAtCursor()
    {
        // NotifyIcon opens its menu only on a right click; the private ShowContextMenu does the
        // focus dance that makes the menu close when the person clicks elsewhere.
        var method = typeof(NotifyIcon).GetMethod("ShowContextMenu", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        if (method is not null) method.Invoke(notifyIcon, null);
        else notifyIcon.ContextMenuStrip?.Show(Cursor.Position);
    }

    private void BuildMenu(ContextMenuStrip menu)
    {
        var state = readState();
        menu.Items.Clear();
        menu.Items.Add(new ToolStripLabel($"● Clicky Bro — {state.StatusText}")
        {
            Font = new Font(SystemFonts.MenuFont ?? Control.DefaultFont, FontStyle.Bold),
            ForeColor = state.StatusText == "Ready" ? Color.FromArgb(0x2E, 0x9E, 0x4F) : Color.FromArgb(0xD9, 0x7A, 0x00),
        });
        menu.Items.Add(new ToolStripLabel($"Hold Ctrl + Win to talk · hold {state.DictationKeyLabel} to dictate") { ForeColor = SystemColors.GrayText });
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(Item("Agent Mode", () => AgentModeToggled?.Invoke(), state.IsAgentModeEnabled));
        menu.Items.Add(Item(state.IslandIsSideDrawer ? "Dock Pointer in the Drawer" : "Dock Pointer in the Island", () => DockToggled?.Invoke(), state.IsCursorDocked));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(Item("Open Clicky Bro", () => OpenWindowRequested?.Invoke()));
        menu.Items.Add(Item("Open the Island", () => OpenIslandRequested?.Invoke()));
        menu.Items.Add(Item("Settings…", () => SettingsRequested?.Invoke(), shortcut: "Ctrl+,"));
        menu.Items.Add(Item("Replay Welcome…", () => ReplayWelcomeRequested?.Invoke()));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(Item("Quit Clicky Bro", () => QuitRequested?.Invoke()));
    }

    private static ToolStripMenuItem Item(string title, Action onClick, bool? isOn = null, string? shortcut = null)
    {
        var item = new ToolStripMenuItem(title) { ShortcutKeyDisplayString = shortcut };
        if (isOn is { } checkedState) item.Checked = checkedState;
        item.Click += (_, _) => onClick();
        return item;
    }

    private static Icon LoadIcon()
    {
        var shipped = Path.Combine(AppContext.BaseDirectory, "Assets", "OpenClicky.ico");
        try
        {
            if (File.Exists(shipped)) return new Icon(shipped, SystemInformation.SmallIconSize);
        }
        catch (Exception error) when (error is ArgumentException or IOException)
        {
            AppLog.Write($"tray: couldn't load {shipped}: {error.Message}");
        }
        return GeneratedMarkIcon();
    }

    /// <summary>The flat navy app tile with its cobalt assistant face and pale-cyan spark, at tray size.</summary>
    public static Icon GeneratedMarkIcon()
    {
        var side = Math.Max(16, SystemInformation.SmallIconSize.Width);
        using var bitmap = new Bitmap(side, side);
        using (var graphics = Graphics.FromImage(bitmap))
        {
            graphics.SmoothingMode = SmoothingMode.AntiAlias;
            graphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
            graphics.Clear(Color.Transparent);
            var tile = new RectangleF(0, 0, side, side);
            using (var background = new SolidBrush(Color.FromArgb(0x13, 0x23, 0x3B)))
            using (var rounded = RoundedRectangle(tile, side * 0.225f))
                graphics.FillPath(background, rounded);

            DrawRounded(graphics, tile, 0.31f, 0.66f, 0.445f, 0.79f, 0.055f, Color.FromArgb(0x2F, 0x81, 0xF7));
            DrawRounded(graphics, tile, 0.555f, 0.66f, 0.69f, 0.79f, 0.055f, Color.FromArgb(0x2F, 0x81, 0xF7));
            DrawRounded(graphics, tile, 0.21f, 0.27f, 0.79f, 0.73f, 0.15f, Color.FromArgb(0x2F, 0x81, 0xF7));
            DrawRounded(graphics, tile, 0.285f, 0.36f, 0.715f, 0.63f, 0.105f, Color.FromArgb(0xF0, 0xF6, 0xFC));
            using (var eyes = new SolidBrush(Color.FromArgb(0x13, 0x23, 0x3B)))
            {
                graphics.FillEllipse(eyes, UnitRect(tile, 0.385f, 0.455f, 0.455f, 0.545f));
                graphics.FillEllipse(eyes, UnitRect(tile, 0.545f, 0.455f, 0.615f, 0.545f));
            }
            using (var spark = SparkPath(tile))
            using (var cyan = new SolidBrush(Color.FromArgb(0xA5, 0xD6, 0xFF)))
                graphics.FillPath(cyan, spark);
        }
        var handle = bitmap.GetHicon();
        // Icon.FromHandle does not own the handle; clone it so the icon outlives the bitmap's handle.
        using var borrowed = Icon.FromHandle(handle);
        var owned = (Icon)borrowed.Clone();
        DestroyIcon(handle);
        return owned;
    }

    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool DestroyIcon(IntPtr handle);

    private static RectangleF UnitRect(RectangleF tile, float x0, float y0, float x1, float y1) =>
        new(tile.Left + x0 * tile.Width, tile.Top + y0 * tile.Height, (x1 - x0) * tile.Width, (y1 - y0) * tile.Height);

    private static void DrawRounded(Graphics graphics, RectangleF tile, float x0, float y0, float x1, float y1, float radius, Color colour)
    {
        using var brush = new SolidBrush(colour);
        using var path = RoundedRectangle(UnitRect(tile, x0, y0, x1, y1), radius * Math.Min(tile.Width, tile.Height));
        graphics.FillPath(brush, path);
    }

    private static GraphicsPath RoundedRectangle(RectangleF bounds, float radius)
    {
        var path = new GraphicsPath();
        var diameter = radius * 2;
        path.AddArc(bounds.X, bounds.Y, diameter, diameter, 180, 90);
        path.AddArc(bounds.Right - diameter, bounds.Y, diameter, diameter, 270, 90);
        path.AddArc(bounds.Right - diameter, bounds.Bottom - diameter, diameter, diameter, 0, 90);
        path.AddArc(bounds.X, bounds.Bottom - diameter, diameter, diameter, 90, 90);
        path.CloseFigure();
        return path;
    }

    /// <summary>The pale-cyan four-point spark shared with OpenClickyMark.swift.</summary>
    private static GraphicsPath SparkPath(RectangleF tile)
    {
        var cx = tile.Left + 0.755f * tile.Width;
        var cy = tile.Top + 0.30f * tile.Height;
        var radius = 0.13f * Math.Min(tile.Width, tile.Height);
        var shoulder = 0.033f * Math.Min(tile.Width, tile.Height);
        var path = new GraphicsPath();
        path.AddPolygon([
            new PointF(cx, cy - radius),
            new PointF(cx + shoulder, cy - shoulder),
            new PointF(cx + radius, cy),
            new PointF(cx + shoulder, cy + shoulder),
            new PointF(cx, cy + radius),
            new PointF(cx - shoulder, cy + shoulder),
            new PointF(cx - radius, cy),
            new PointF(cx - shoulder, cy - shoulder),
        ]);
        return path;
    }

    public void Dispose()
    {
        notifyIcon.Visible = false;
        notifyIcon.Dispose();
        icon.Dispose();
    }
}
