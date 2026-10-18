"""Enforce Clicky Bro Azure colour contrast and macOS/Windows token parity."""
from __future__ import annotations

import json
import re
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MAC = ROOT / "app/macos/OpenClicky/OpenClicky/DesignSystem.swift"
WINDOWS = ROOT / "app/windows/src/OpenClicky.Windows/Theme/DS.cs"
XAML = ROOT / "app/windows/src/OpenClicky.Windows/Theme/OpenClickyTheme.xaml"
MANIFEST = ROOT / "design/tokens.json"
REQUIRED = {"Canvas", "Surface", "SurfaceRaised", "PrimaryText", "SecondaryText", "Border", "Accent"}


def luminance(hex_value: str) -> float:
    def channel(v: int) -> float:
        n = v / 255
        return n / 12.92 if n <= 0.04045 else ((n + 0.055) / 1.055) ** 2.4
    red, green, blue = (channel(int(hex_value[i:i + 2], 16)) for i in (1, 3, 5))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    a, b = sorted((luminance(first), luminance(second)), reverse=True)
    return (a + 0.05) / (b + 0.05)


class AzureDesignTokensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.mac = MAC.read_text(encoding="utf-8")
        cls.win = WINDOWS.read_text(encoding="utf-8")
        cls.xaml = XAML.read_text(encoding="utf-8")
        cls.xaml_root = ET.fromstring(cls.xaml)

    def test_complete_valid_palette(self):
        self.assertEqual(self.data["version"], 1)
        for theme in ("light", "dark"):
            self.assertEqual(set(self.data[theme]), REQUIRED)
            for color in self.data[theme].values():
                self.assertRegex(color, r"^#[0-9A-F]{6}$")

    def test_accessible_body_and_controls(self):
        for theme in ("light", "dark"):
            palette = self.data[theme]
            self.assertGreaterEqual(contrast(palette["PrimaryText"], palette["Surface"]), 7)
            self.assertGreaterEqual(contrast(palette["SecondaryText"], palette["Surface"]), 4.5)
            self.assertGreaterEqual(contrast(palette["Accent"], palette["Surface"]), 4.5)

    def test_swift_tokens_match_manifest(self):
        self.assertIn("NSColor(name: nil)", self.mac)
        self.assertIn("appearance.bestMatch", self.mac)
        for theme in ("light", "dark"):
            for name, color in self.data[theme].items():
                key = name[0].lower() + name[1:]
                self.assertIn(f"{key} = adaptive(", self.mac)
                self.assertIn("0x" + color[1:], self.mac)

    def test_windows_code_and_xaml_match_manifest(self):
        ns = {"x": "http://schemas.microsoft.com/winfx/2006/xaml"}
        values = {
            element.attrib.get("{http://schemas.microsoft.com/winfx/2006/xaml}Key"): (element.text or "").strip()
            for element in self.xaml_root.iter()
        }
        for theme in ("light", "dark"):
            group = "AzureLight" if theme == "light" else "AzureDark"
            self.assertIn(f"class {group}", self.win)
            for name, color in self.data[theme].items():
                self.assertIn(f"{name} = Hex(\"{color}\")", self.win)
                self.assertEqual(values[f"ClickyBro.Azure.{theme.title()}.{name}Color"], "#FF" + color[1:])

    def test_pointer_color_parity(self):
        pointer = self.data["overlays"]["pointer"]
        self.assertIn(f"overlayCursorColor = Color(hex: \"{pointer}\")", self.mac)
        self.assertIn(f"OverlayCursor = Hex(\"{pointer}\")", self.win)
        self.assertIn("#FF" + pointer[1:], self.xaml)


if __name__ == "__main__":
    unittest.main()
