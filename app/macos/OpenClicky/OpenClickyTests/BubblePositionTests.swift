import Testing
@testable import OpenClicky

struct BubblePositionTests {
    @Test func keepsSmallBubblesInsideEdges() {
        #expect(BubblePosition.center(preferred: -40, extent: 120, screenExtent: 800) == 68)
        #expect(BubblePosition.center(preferred: 999, extent: 120, screenExtent: 800) == 732)
        #expect(BubblePosition.center(preferred: 300, extent: 120, screenExtent: 800) == 300)
    }

    @Test func handlesShortScreensAndOversizedCaptions() {
        #expect(BubblePosition.center(preferred: 100, extent: 350, screenExtent: 300) == 150)
        #expect(BubblePosition.center(preferred: -1, extent: 10, screenExtent: 12) == 13)
    }
}
