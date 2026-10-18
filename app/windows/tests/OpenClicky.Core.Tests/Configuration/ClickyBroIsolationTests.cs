using OpenClicky.Core.Configuration;

namespace OpenClicky.Core.Tests.Configuration;

public sealed class ClickyBroIsolationTests
{
    [Fact]
    public void DefaultsArePrivateAndGeminiCredentialDoesNotNeedOpenAi()
    {
        Assert.EndsWith(".clicky-bro", OpenClickyPaths.SettingsDirectory);
        Assert.EndsWith("clicky-bro", OpenClickyPaths.AppDataDirectory);
        var settings = new OpenClickyShellSettings { GeminiApiKey = "test-only" };
        Assert.Equal("gemini", settings.AnswerSource);
        Assert.Equal("http://127.0.0.1:18787", settings.BackendUrl);
        var environment = OpenClickyConfiguration.CliProcessEnvironmentFor(settings, new Dictionary<string, string>());
        Assert.Equal("test-only", environment["CLICKY_BRO_GEMINI_KEY"]);
        Assert.Equal("gemini-3.5-flash-lite", environment["CLICKY_BRO_GEMINI_MODEL"]);
        Assert.True(OpenClickyConfiguration.UsesOwnKeysFor(settings));
    }

    [Fact]
    public void ExplicitKeyFileLoadsWithoutReadingAnotherApplicationsSettings()
    {
        var directory = Path.Combine(Path.GetTempPath(), "clicky-bro-key-" + Guid.NewGuid()); Directory.CreateDirectory(directory);
        try
        {
            var file = Path.Combine(directory, "key.json"); File.WriteAllText(file, "{\"api_key\":\"test-only\"}");
            if (!OperatingSystem.IsWindows()) File.SetUnixFileMode(file, UnixFileMode.UserRead | UnixFileMode.UserWrite);
            var settings = OpenClickyConfiguration.Load(Path.Combine(directory, "missing-shell.json"), new Dictionary<string, string> { ["CLICKY_BRO_GEMINI_KEY_FILE"] = file });
            Assert.Equal("test-only", settings.GeminiApiKey);
            Assert.False(File.Exists(Path.Combine(directory, "missing-shell.json")));
        }
        finally { Directory.Delete(directory, true); }
    }
}
