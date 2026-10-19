namespace OpenClicky.Core.Pointing;

/// <summary>Pure native-overlay layout contract, independent of WPF and display scale.</summary>
public static class OverlayBubbleGeometry
{
    /// <summary>Clamp a top/left corner within the visible monitor bounds.
    /// Oversized bubbles stay anchored at 0 rather than overflowing to a negative origin.</summary>
    public static double Offset(double proposed, double bubbleExtent, double screenExtent)
    {
        if (!double.IsFinite(proposed) || !double.IsFinite(bubbleExtent) || !double.IsFinite(screenExtent)) return 0;
        var extent = Math.Max(0, bubbleExtent);
        var screen = Math.Max(0, screenExtent);
        if (extent >= screen) return 0;
        var lower = Math.Min(8, screen - extent);
        var upper = Math.Max(lower, screen - extent - 8);
        return Math.Clamp(proposed, lower, upper);
    }
}
