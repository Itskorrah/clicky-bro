import Foundation

/// Pure placement math for the existing native companion UI.
enum BubblePosition {
    /// SwiftUI .position uses centres; prefer a small inset when the bubble fits.
    static func center(preferred: CGFloat, extent: CGFloat, screenExtent: CGFloat) -> CGFloat {
        guard preferred.isFinite, extent.isFinite, screenExtent.isFinite else { return 0 }
        if extent >= screenExtent { return max(0, screenExtent / 2) }
        let half = max(0, extent / 2)
        let lower = half + 8
        let upper = max(lower, screenExtent - half - 8)
        return min(max(preferred, lower), upper)
    }
}
