"""Public branding assertions; compatibility identifiers must not be renamed accidentally."""
from pathlib import Path
import plistlib
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class PublicBrandingTests(unittest.TestCase):
    def test_original_logo_and_readme_link(self):
        icon = ROOT / "docs/assets/clicky-bro-mark.svg"
        root = ET.parse(icon).getroot()
        self.assertEqual(root.get("viewBox"), "0 0 512 512")
        self.assertIn('docs/assets/clicky-bro-mark.svg', (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_user_facing_window_titles(self):
        required = {
            "app/macos/OpenClicky/OpenClicky/OverlayWindow.swift": 'Hi, I\'m Clicky Bro.',
            "app/macos/OpenClicky/OpenClicky/Dictation/UI/DictationWindow.swift": 'window.title = "Clicky Bro"',
            "app/windows/src/OpenClicky.Windows/Overlay/OverlayWindow.cs": 'Hi, I\'m Clicky Bro.',
            "app/windows/src/OpenClicky.Windows/MainWindow/DictationWindow.cs": 'Title = "Clicky Bro"',
            "app/windows/src/OpenClicky.Windows/Tray/TrayIcon.cs": 'Text = "Clicky Bro"'
        }
        for name, text in required.items():
            with self.subTest(name=name):
                self.assertIn(text, (ROOT / name).read_text(encoding="utf-8"))

    def test_compatibility_identity_and_permission_copy(self):
        project = (ROOT / "app/macos/OpenClicky/OpenClicky.xcodeproj/project.pbxproj").read_text(encoding="utf-8")
        self.assertIn("PRODUCT_NAME = OpenClicky;", project)
        self.assertIn("PRODUCT_BUNDLE_IDENTIFIER = dev.clicky-bro.app;", project)
        self.assertEqual(project.count('INFOPLIST_KEY_CFBundleDisplayName = "Clicky Bro";'), 2)
        plist = plistlib.loads((ROOT / "app/macos/OpenClicky/OpenClicky/Info.plist").read_bytes())
        self.assertIn("Clicky Bro", plist["NSScreenCaptureUsageDescription"])
        swift = (ROOT / "app/macos/OpenClicky/OpenClicky/Dictation/DictationSettings.swift").read_text(encoding="utf-8")
        self.assertIn("case openclicky", swift)
        windows = (ROOT / "app/windows/src/OpenClicky.Core/Dictation/DictationSettings.cs").read_text(encoding="utf-8")
        self.assertIn('[RawValue("clicky-bro")] OpenClicky', windows)

if __name__ == "__main__":
    unittest.main()
