using OpenClicky.Core.Actions;

namespace OpenClicky.Core.Tests.Actions;

public sealed class HostActionAuthorizationTests
{
    [Fact]
    public async Task MissingDeclinedOrFailedConfirmationCannotExecuteAnAction()
    {
        var executions = 0;
        Task<string> Execute() { executions++; return Task.FromResult("performed"); }
        Assert.Contains("denied", await HostActionAuthorization.ExecuteAsync("set volume", null, Execute, default));
        Assert.Contains("declined", await HostActionAuthorization.ExecuteAsync("set volume", (_, _) => Task.FromResult(false), Execute, default));
        Assert.Contains("denied", await HostActionAuthorization.ExecuteAsync("set volume", (_, _) => throw new InvalidOperationException("UI unavailable"), Execute, default));
        Assert.Equal(0, executions);
    }

    [Fact]
    public async Task CancellationDuringApprovalCannotExecuteEvenAfterAnAllowResponse()
    {
        var executions = 0; using var cancellation = new CancellationTokenSource();
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => HostActionAuthorization.ExecuteAsync("set volume",
            (_, _) => { cancellation.Cancel(); return Task.FromResult(true); },
            () => { executions++; return Task.FromResult("performed"); }, cancellation.Token));
        Assert.Equal(0, executions);
    }

    [Fact]
    public async Task OneUserApprovalPermitsExactlyTheProposedAction()
    {
        var seen = ""; var executions = 0;
        var outcome = await HostActionAuthorization.ExecuteAsync("set volume: 40",
            (details, _) => { seen = details; return Task.FromResult(true); },
            () => { executions++; return Task.FromResult("actual volume: 40"); }, default);
        Assert.Equal("set volume: 40", seen); Assert.Equal(1, executions); Assert.Equal("actual volume: 40", outcome);
    }
}
