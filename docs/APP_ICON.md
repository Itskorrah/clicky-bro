# Clicky Bro app icon

The icon now uses a flat deep-navy tile with a cobalt assistant face, pale faceplate and small cyan spark. The tile is blue enough to stay distinct on dark system surfaces. The mascot and spark keep the Clicky Bro companion identity while removing the former beveled tile, coral ring and pointer. The mark uses no GitHub logos or Octocat artwork.

## Palette and geometry

- Navy tile and eye details: `#13233B`
- Cobalt head and feet: `#2F81F7`
- Pale-cyan four-point spark: `#A5D6FF`
- Faceplate: `#F0F6FC`

The app icon, macOS status item and Windows tray use the same navy tile, assistant face, faceplate and cyan spark. The Windows WPF title bar and privacy page use the same artwork. The menu-bar version draws the tile within its native status-item bounds; app-icon files keep their platform-specific transparent margin. The broad shapes and high-contrast face were reviewed at 16 px and 32 px on light and dark surrounding surfaces.

## Source and regeneration

`app/macos/OpenClicky/scripts/make-app-icon.py` is the editable, deterministic source for the macOS `AppIcon.appiconset` PNGs. It draws each supported size directly with supersampling so the small assets keep their transparent icon-grid margin. `app/windows/scripts/make-app-icon.ps1` crops the 1024 px macOS master to its opaque square and writes the Windows multi-size ICO.

The macOS generator requires Pillow in the Python environment used to run it.

Regenerate the macOS assets from the repository root:

```bash
python3 app/macos/OpenClicky/scripts/make-app-icon.py
```

On Windows, regenerate the ICO from that 1024 px source:

```powershell
pwsh app/windows/scripts/make-app-icon.ps1
```

For this change, the ICO was generated from the same 1024 px master with Pillow because PowerShell was unavailable on the authoring host. It contains 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256 px PNG-compressed entries.

## Artwork provenance

Two original built-in ImageGen concepts were explored on 2026-10-19:

- Friendly assistant face and spark: `/Users/korrah/.codex/generated_images/01a15365-52fe-7dc3-a19c-cebd84484d48/exec-80b01199-54df-4c1b-ae75-da757ab4462c.png`
- Abstract four-point click spark: `/Users/korrah/.codex/generated_images/01a15365-52fe-7dc3-a19c-cebd84484d48/exec-1b83e201-4192-4f28-9bca-a30c44bdf4fb.png`

The friendly concept informed the selected direction. The generated files remain concept references outside the repository: the first had raster shading and an irregular subject crop, and the second was a generic detached sparkle. The final geometry is hand-authored in the code generators so each platform can render it consistently at small sizes and edit it without depending on a generated bitmap.
