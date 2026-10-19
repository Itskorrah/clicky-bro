//
//  OpenClickyMark.swift
//  OpenClicky
//
//  The small, full-colour Clicky Bro companion mark used by the macOS status item. Its normalized
//  shapes match make-app-icon.py and OpenClickyMarkDrawing in the Windows client.
//

import AppKit

enum OpenClickyMark {
    private static let ink = NSColor(srgbRed: 19.0 / 255.0, green: 35.0 / 255.0, blue: 59.0 / 255.0, alpha: 1)
    private static let cobalt = NSColor(srgbRed: 47.0 / 255.0, green: 129.0 / 255.0, blue: 247.0 / 255.0, alpha: 1)
    private static let paleCyan = NSColor(srgbRed: 165.0 / 255.0, green: 214.0 / 255.0, blue: 255.0 / 255.0, alpha: 1)
    private static let paper = NSColor(srgbRed: 240.0 / 255.0, green: 246.0 / 255.0, blue: 252.0 / 255.0, alpha: 1)

    /// Draw the navy app tile, companion face and attached four-point spark into a flipped (y-down) rect.
    @discardableResult
    static func draw(in rect: CGRect) -> Bool {
        let side = min(rect.width, rect.height)
        let tile = CGRect(x: rect.midX - side / 2, y: rect.midY - side / 2, width: side, height: side)
        func box(_ x0: CGFloat, _ y0: CGFloat, _ x1: CGFloat, _ y1: CGFloat) -> CGRect {
            CGRect(
                x: tile.minX + x0 * side,
                y: tile.minY + y0 * side,
                width: (x1 - x0) * side,
                height: (y1 - y0) * side
            )
        }
        func rounded(_ x0: CGFloat, _ y0: CGFloat, _ x1: CGFloat, _ y1: CGFloat, _ radius: CGFloat) -> NSBezierPath {
            NSBezierPath(roundedRect: box(x0, y0, x1, y1), xRadius: radius * side, yRadius: radius * side)
        }

        ink.setFill()
        rounded(0, 0, 1, 1, 0.22).fill()

        cobalt.setFill()
        rounded(0.31, 0.66, 0.445, 0.79, 0.055).fill()
        rounded(0.555, 0.66, 0.69, 0.79, 0.055).fill()
        rounded(0.21, 0.27, 0.79, 0.73, 0.15).fill()

        paper.setFill()
        rounded(0.285, 0.36, 0.715, 0.63, 0.105).fill()

        ink.setFill()
        NSBezierPath(ovalIn: box(0.385, 0.455, 0.455, 0.545)).fill()
        NSBezierPath(ovalIn: box(0.545, 0.455, 0.615, 0.545)).fill()

        paleCyan.setFill()
        sparkPath(in: tile).fill()
        return true
    }

    private static func sparkPath(in rect: CGRect) -> NSBezierPath {
        let side = min(rect.width, rect.height)
        let cx = rect.midX + (0.755 - 0.5) * side
        let cy = rect.minY + 0.30 * side
        let radius = 0.13 * side
        let shoulder = 0.033 * side
        let points = [
            CGPoint(x: cx, y: cy - radius),
            CGPoint(x: cx + shoulder, y: cy - shoulder),
            CGPoint(x: cx + radius, y: cy),
            CGPoint(x: cx + shoulder, y: cy + shoulder),
            CGPoint(x: cx, y: cy + radius),
            CGPoint(x: cx - shoulder, y: cy + shoulder),
            CGPoint(x: cx - radius, y: cy),
            CGPoint(x: cx - shoulder, y: cy - shoulder),
        ]
        let path = NSBezierPath()
        path.move(to: points[0])
        for point in points.dropFirst() { path.line(to: point) }
        path.close()
        return path
    }
}
