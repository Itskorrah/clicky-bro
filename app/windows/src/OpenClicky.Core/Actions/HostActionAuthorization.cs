namespace OpenClicky.Core.Actions;

/// <summary>The host owns authorization; model output and Agent mode alone cannot approve an action.</summary>
public static class HostActionAuthorization
{
    public static async Task<string> ExecuteAsync(string details,
        Func<string, CancellationToken, Task<bool>>? confirm,
        Func<Task<string>> execute, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (confirm is null) return "Action denied: host confirmation is unavailable. Nothing was changed.";
        bool approved;
        try { approved = await confirm(details, cancellationToken).ConfigureAwait(false); }
        catch (OperationCanceledException) { throw; }
        catch { return "Action denied: confirmation failed. Nothing was changed."; }
        cancellationToken.ThrowIfCancellationRequested();
        if (!approved) return "Action declined by you. Nothing was changed.";
        return await execute().ConfigureAwait(false);
    }
}
