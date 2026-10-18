using System.Windows;
using System.Windows.Controls;

namespace OpenClicky.Windows.Companion;

/// <summary>A cancellable native host prompt; only the user's Allow click authorizes one action.</summary>
public static class ActionConfirmationWindow
{
    public static async Task<bool> ConfirmAsync(string details, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var completion = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        Window? window = null;
        var dispatcher = Application.Current.Dispatcher;
        await dispatcher.InvokeAsync(() =>
        {
            cancellationToken.ThrowIfCancellationRequested();
            var content = new StackPanel { Margin = new Thickness(20) };
            content.Children.Add(new TextBlock { Text = "Allow clicky-bro to perform this action?", TextWrapping = TextWrapping.Wrap, FontSize = 18, Margin = new Thickness(0, 0, 0, 12) });
            content.Children.Add(new TextBox { Text = details, IsReadOnly = true, TextWrapping = TextWrapping.Wrap, MaxHeight = 300, VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Margin = new Thickness(0, 0, 0, 16) });
            var buttons = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right };
            var deny = new Button { Content = "Cancel", MinWidth = 90, Padding = new Thickness(10, 6, 10, 6), IsDefault = true, Margin = new Thickness(0, 0, 8, 0) };
            var allow = new Button { Content = "Allow once", MinWidth = 90, Padding = new Thickness(10, 6, 10, 6) };
            window = new Window { Title = "clicky-bro — action permission", Content = content, Width = 500, SizeToContent = SizeToContent.Height, ResizeMode = ResizeMode.NoResize, WindowStartupLocation = WindowStartupLocation.CenterScreen, Topmost = true };
            deny.Click += (_, _) => { completion.TrySetResult(false); window.Close(); };
            allow.Click += (_, _) => { if (!cancellationToken.IsCancellationRequested) completion.TrySetResult(true); window.Close(); };
            window.Closed += (_, _) => completion.TrySetResult(false);
            buttons.Children.Add(deny); buttons.Children.Add(allow); content.Children.Add(buttons);
            window.Show();
        });
        using var cancellation = cancellationToken.Register(() => dispatcher.InvokeAsync(() =>
        {
            completion.TrySetCanceled(cancellationToken);
            window?.Close();
        }));
        var approved = await completion.Task.ConfigureAwait(false);
        cancellationToken.ThrowIfCancellationRequested();
        return approved;
    }
}
