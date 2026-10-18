// Port of macos/OpenClicky/OpenClickyTests/WriteInPlaceTests.swift (+ the Farewell test from
// HUDPlacementTests and a test of the ported replace flow over a fake host).
// theQuestionCarriesTheExactWords (CompanionManager.askUserPrompt) is in AskLaneTests.cs (AskLanePrompts.AskUserPrompt).

using OpenClicky.Core.Answers;

namespace OpenClicky.Core.Tests.Answers;

public class WriteInPlaceTests
{
    private static WritingFieldSnapshot Field(string? value = null, string? selected = null, bool editable = true, bool secure = false,
                                              string app = "chrome.exe") =>
        new(app, "Google Chrome", "Edit", editable, secure, value, selected, "field-1", 42, selected is null ? null : value?.IndexOf(selected, StringComparison.Ordinal) ?? 0, selected?.Length);

    [Fact]
    public void AHighlightIsTheTarget()
    {
        var target = WritingTarget.Target(Field(value: "Hi Ravi, see you at 5. Amma", selected: "see you at 5."), ownProcessName: "clicky-bro.exe");
        Assert.Equal(WritingScope.Selection, target?.Scope);
        Assert.Equal("see you at 5.", target?.Text);
    }

    [Fact]
    public void WithoutAHighlightTheWholeBoxIsTheTarget()
    {
        var target = WritingTarget.Target(Field(value: "Hi Ravi,\nsee you at 5.\nAmma"), ownProcessName: "clicky-bro.exe");
        Assert.Equal(WritingScope.WholeField, target?.Scope);
        Assert.Equal("Hi Ravi,\nsee you at 5.\nAmma", target?.Text);
    }

    [Fact]
    public void NothingToRewriteMeansNoTarget()
    {
        Assert.Null(WritingTarget.Target(Field(value: "   "), ownProcessName: "x"));
        Assert.Null(WritingTarget.Target(Field(value: "secret", secure: true), ownProcessName: "x"));
        Assert.Null(WritingTarget.Target(Field(value: "a page", editable: false), ownProcessName: "x"));
        Assert.Null(WritingTarget.Target(Field(value: "my own window", app: "clicky-bro.exe"), ownProcessName: "clicky-bro.exe"));
        Assert.Null(WritingTarget.Target(Field(value: "my own window", app: "clicky-bro"), ownProcessName: "clicky-bro.exe"));
        Assert.Null(WritingTarget.Target(Field(value: new string('a', WritingTarget.MaximumCharacters + 1)), ownProcessName: "x"));
    }

    [Fact]
    public void ItIsOnlyPastedIntoTheSameTextStill()
    {
        var target = new WritingTarget(WritingScope.WholeField, "Hi Ravi", "chrome.exe", "Google Chrome", "field-1", 42);
        Assert.True(target.StillMatches(Field(value: "Hi Ravi")));
        Assert.False(target.StillMatches(Field(value: "Hi Ravi, also")));
        Assert.False(target.StillMatches(Field(value: "Hi Ravi", app: "outlook.exe")));
        Assert.False(target.StillMatches(Field(value: "Hi Ravi", editable: false)));
        var highlighted = WritingTarget.Target(Field(value: "see you at 5", selected: "at 5"))!;
        Assert.True(highlighted.StillMatches(Field(value: "see you at 5", selected: "at 5")));
        Assert.False(highlighted.StillMatches(Field(value: "see you at 5", selected: null)));
    }

    [Fact]
    public void TheContextLineCarriesTheExactWordsAndTheApp()
    {
        var target = new WritingTarget(WritingScope.WholeField, "Hi Ravi,\nsee you at 5.", "chrome.exe", "Google Chrome", "field-1", 42);
        Assert.Contains("Hi Ravi,\nsee you at 5.", target.ContextLine);
        Assert.Contains("in Google Chrome", target.ContextLine);
        Assert.Contains(WriteInPlace.ToolName, target.ContextLine);
    }

    [Fact]
    public void TheToolAsksForTheWholeNewText()
    {
        var definition = WriteInPlace.AnthropicToolDefinition();
        Assert.Equal("write_in_place", (string?)definition["name"]);
        var required = definition["input_schema"]!["required"]!.AsArray().Select(node => (string?)node).ToArray();
        Assert.Equal(new[] { "text" }, required);
    }

    [Fact]
    public void TheRewriteKeepsTheSpacingAroundTheOldText()
    {
        Assert.Equal("Sorry for the delay.\n", WriteInPlace.KeepingSurroundingSpace("sorry it took long.\n", "Sorry for the delay."));
        Assert.Equal(" at five", WriteInPlace.KeepingSurroundingSpace(" at 5", "\nat five\n"));
        Assert.Equal("Hi Ravi,", WriteInPlace.KeepingSurroundingSpace("hi ravi", "Hi Ravi,"));
    }

    [Fact]
    public void EachOutcomeSaysWhatHappened()
    {
        Assert.Contains("control z", WriteInPlaceOutcome.Replaced.SpokenSentence());
        Assert.Contains("didn't change anything", WriteInPlaceOutcome.TargetGone.SpokenSentence());
        Assert.False(WriteInPlaceOutcome.TargetGone.DidReplace());
        foreach (var outcome in Enum.GetValues<WriteInPlaceOutcome>())
        {
            Assert.DoesNotContain("—", outcome.SpokenSentence());
        }
    }

    private sealed class FakeHost : IWriteInPlaceHost
    {
        public WritingFieldSnapshot Snapshot { get; set; } = Field(value: "Hi Ravi");
        public WriteInPlaceLanding Landing { get; set; } = WriteInPlaceLanding.Verified;
        public List<string> Steps { get; } = new();
        public bool CanReadFocusedFields => true;
        public bool IsOwnProcessInFront() => false;
        public WritingFieldSnapshot SnapshotFocusedField() => Snapshot;
        public void SelectAllInFocusedField()
        {
            Steps.Add("select all");
            Snapshot = Snapshot with { SelectedText = Snapshot.Value, SelectionStart = 0, SelectionLength = Snapshot.Value?.Length };
        }
        public void Insert(string text) => Steps.Add("insert " + text);
        public Task<WriteInPlaceLanding> VerifyLandingAsync(string text, WritingFieldSnapshot before, CancellationToken cancellationToken = default) => Task.FromResult(Landing);
        public void CopyToClipboard(string text) => Steps.Add("copy " + text);
    }

    [Fact]
    public async Task ReplacingSelectsTheWholeBoxPastesAndLeavesTheOriginalOnTheClipboard()
    {
        var host = new FakeHost();
        var target = new WritingTarget(WritingScope.WholeField, "Hi Ravi", "chrome.exe", "Google Chrome", "field-1", 42);
        var outcome = await WriteInPlace.ReplaceAsync(target, "Hello Ravi", host, delay: _ => Task.CompletedTask);
        Assert.Equal(WriteInPlaceOutcome.Replaced, outcome);
        Assert.Equal(new[] { "select all", "insert Hello Ravi", "copy Hi Ravi" }, host.Steps);
    }

    [Fact]
    public async Task NothingIsPastedOnceTheTargetMoved()
    {
        var host = new FakeHost { Snapshot = Field(value: "something else") };
        var target = new WritingTarget(WritingScope.WholeField, "Hi Ravi", "chrome.exe", "Google Chrome", "field-1", 42);
        Assert.Equal(WriteInPlaceOutcome.TargetGone, await WriteInPlace.ReplaceAsync(target, "Hello", host, delay: _ => Task.CompletedTask));
        Assert.Empty(host.Steps);
        Assert.Equal(WriteInPlaceOutcome.EmptyText, await WriteInPlace.ReplaceAsync(target, "  ", host, delay: _ => Task.CompletedTask));
    }

    [Fact]
    public async Task NoTargetAfterThePasteLeavesTheNewTextOnTheClipboard()
    {
        var host = new FakeHost { Landing = WriteInPlaceLanding.NoTarget };
        host.Snapshot = Field(value: "x Hi Ravi", selected: "Hi Ravi");
        var target = WritingTarget.Target(host.Snapshot)!;
        Assert.Equal(WriteInPlaceOutcome.LeftOnClipboard, await WriteInPlace.ReplaceAsync(target, "Hello", host, delay: _ => Task.CompletedTask));
        Assert.Equal(new[] { "insert Hello" }, host.Steps);
    }

    [Fact]
    public async Task ChangingCaretInsideTheSameBoxDuringSelectDelayDoesNotAppend()
    {
        var host = new FakeHost(); var target = WritingTarget.Target(host.Snapshot)!;
        var result = await WriteInPlace.ReplaceAsync(target, "Hello", host,
            delay: _ => { host.Snapshot = host.Snapshot with { SelectedText = null, SelectionLength = 0 }; return Task.CompletedTask; });
        Assert.Equal(WriteInPlaceOutcome.TargetGone, result);
        Assert.Equal(new[] { "select all" }, host.Steps);
    }

    [Fact]
    public void IdenticalWordsAtAnotherSelectionOffsetAreNotTheSameTarget()
    {
        var snapshot = Field(value: "hello hello", selected: "hello");
        var target = WritingTarget.Target(snapshot)!;
        Assert.False(target.StillMatches(snapshot with { SelectionStart = 6 }));
    }

    [Fact]
    public async Task StopDuringSelectAllDelayPreventsInsertionAndClipboardChanges()
    {
        var host = new FakeHost(); var target = WritingTarget.Target(host.Snapshot)!;
        using var stop = new CancellationTokenSource();
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => WriteInPlace.ReplaceAsync(target, "Hello", host,
            delay: _ => { stop.Cancel(); return Task.CompletedTask; }, cancellationToken: stop.Token));
        Assert.Equal(new[] { "select all" }, host.Steps);
    }

    [Fact]
    public async Task MovingToADifferentFieldWithIdenticalWordsDuringSelectDelayNeverInserts()
    {
        var host = new FakeHost(); var target = WritingTarget.Target(host.Snapshot)!;
        var result = await WriteInPlace.ReplaceAsync(target, "Hello", host,
            delay: _ => { host.Snapshot = host.Snapshot with { RuntimeId = "other-field" }; return Task.CompletedTask; });
        Assert.Equal(WriteInPlaceOutcome.TargetGone, result);
        Assert.Equal(new[] { "select all" }, host.Steps);
    }

    [Fact]
    public async Task StopAfterInsertionPreventsDelayedClipboardRestoration()
    {
        var host = new FakeHost(); var target = WritingTarget.Target(host.Snapshot)!;
        using var stop = new CancellationTokenSource();
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => WriteInPlace.ReplaceAsync(target, "Hello", host,
            delay: time => { if (time.TotalMilliseconds == 400) stop.Cancel(); return Task.CompletedTask; }, cancellationToken: stop.Token));
        Assert.Equal(new[] { "select all", "insert Hello" }, host.Steps);
    }

    [Fact]
    public async Task MovingFocusAfterInsertionPreventsDelayedClipboardRestoration()
    {
        var host = new FakeHost(); var target = WritingTarget.Target(host.Snapshot)!;
        var result = await WriteInPlace.ReplaceAsync(target, "Hello", host,
            delay: time => { if (time.TotalMilliseconds == 400) host.Snapshot = host.Snapshot with { RuntimeId = "other-field" }; return Task.CompletedTask; });
        Assert.Equal(WriteInPlaceOutcome.Replaced, result);
        Assert.Equal(new[] { "select all", "insert Hello" }, host.Steps);
    }

    [Fact]
    public void MissingElementIdentityCannotBecomeARewriteTarget()
    {
        Assert.Null(WritingTarget.Target(Field(value: "hello") with { RuntimeId = null }));
    }

    // From HUDPlacementTests.swift: everyGoodbyeSaysHowToComeBackOrIsShort (Windows wording).
    [Fact]
    public void EveryGoodbyeSaysHowToComeBackOrIsShort()
    {
        foreach (var farewell in Farewell.All)
        {
            Assert.True(farewell.Text.Contains("clicky-bro") || farewell.Text.Contains("windows key"), farewell.Text);
            Assert.True(farewell.Text.Length <= 90, farewell.Text);
        }
        Assert.Contains(Farewell.Random(), Farewell.All);
    }
}
