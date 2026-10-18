"""Prevent regression to automatic Parakeet downloads after selecting an engine."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAC_MODEL = ROOT / "app/macos/OpenClicky/OpenClicky/Parakeet/ParakeetDictation.swift"
MAC_UI = ROOT / "app/macos/OpenClicky/OpenClicky/Dictation/UI/SettingsDictationPage.swift"
WIN_MODEL = ROOT / "app/windows/src/OpenClicky.Core/Speech/ParakeetDictation.cs"
WIN_UI = ROOT / "app/windows/src/OpenClicky.Windows/MainWindow/SettingsDictationPage.cs"


class ExplicitModelDownloadTests(unittest.TestCase):
    def test_mac_has_an_explicit_download_button_and_no_selection_side_effect(self):
        ui = MAC_UI.read_text(encoding="utf-8")
        self.assertIn('Button("Download \\(ParakeetDictation.downloadSizeText)") { parakeet.download() }', ui)
        self.assertNotIn('if choice == .parakeet { ParakeetDictation.shared.download() }', ui)

    def test_win_has_explicit_download_button_and_no_selection_side_effect(self):
        ui = WIN_UI.read_text(encoding="utf-8")
        self.assertIn('Ui.Button($"Download {model.DownloadSizeText}", model.Download)', ui)
        self.assertNotIn('if (choice == DictationEngineChoice.Parakeet && parakeet.State.Kind == ModelDownloadState.Stage.NotInstalled) parakeet.Download()', ui)

    def test_startup_compatibility_callbacks_are_network_inert(self):
        for source, signature, end in [
            (MAC_MODEL, "func startAutomaticSetup(", "/// The engine once an automatic download finishes:"),
            (WIN_MODEL, "public void StartAutomaticSetup(bool tourIsFinished, string currentEngineRawValue,", "/// <summary>The engine once an automatic download finishes:"),
        ]:
            text = source.read_text(encoding="utf-8")
            start = text.index(signature)
            stop = text.index(end, start)
            body = text[start:stop]
            self.assertNotRegex(body, r"(?:\bdownload\(|\bDownload\(|\bnetworkIsExpensive|\bNetworkIsExpensive)")
            self.assertIn("No ", body) if source == MAC_MODEL else self.assertIn("Intentionally inert", body)


if __name__ == "__main__":
    unittest.main()
