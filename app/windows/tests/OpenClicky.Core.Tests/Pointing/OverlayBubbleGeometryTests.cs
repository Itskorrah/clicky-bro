using OpenClicky.Core.Pointing;

namespace OpenClicky.Core.Tests.Pointing;

public sealed class OverlayBubbleGeometryTests
{
    [Theory]
    [InlineData(-40, 120, 800, 8)]
    [InlineData(999, 120, 800, 672)]
    [InlineData(300, 120, 800, 300)]
    [InlineData(100, 350, 300, 0)]
    [InlineData(99, 10, 12, 2)]
    public void ClampsBubblesInsideMonitor(double proposed, double size, double screen, double expected)
        => Assert.Equal(expected, OverlayBubbleGeometry.Offset(proposed, size, screen));

    [Fact]
    public void HandlesNonFiniteInput()
    {
        Assert.Equal(0, OverlayBubbleGeometry.Offset(double.NaN, 100, 800));
        Assert.Equal(0, OverlayBubbleGeometry.Offset(10, 100, double.PositiveInfinity));
    }
}
