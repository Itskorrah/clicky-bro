import Foundation

/// Pure placement math for the existing native companion UI.
enum BubblePosition {
    /// SwiftUI .position uses centres; prefer a small inset when the bubble fits.
    static func center(preferred: CGFloat, extent: CGFloat, screenExtent: CGFloat) -> CGFloat {
        guard preferred.isFinite, extent.isFinite, screenExtent.isFinite else { return 0 }
        let half = max(0, extent / 2)
        let lower = min(half + 8, max(half, screenExtent / 2))
        let upper = max(lower, screenExtent - half - 8)
        return min(max(preferred, lower), upper)
    }
}
