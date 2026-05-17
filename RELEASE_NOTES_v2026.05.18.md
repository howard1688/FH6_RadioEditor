# FH6 Radio Editor v2026.05.18

## Highlights

- Added a lightweight release package
- `radio_editor.exe` now works with external `ffmpeg.exe` and `fmod tool/`
- Reduced release zip size significantly by removing bundled FMOD tool files and ffmpeg from the packaged build
- Updated README with release usage notes and workflow documentation

## Lightweight Release Layout

The lightweight release zip now includes:

- `radio_editor.exe`
- `_internal/`
- `README.md`
- `README.en.md`
- `RELEASE_FILES.txt`

Users should also place these next to `radio_editor.exe`:

- `ffmpeg.exe`
- `fmod tool/`

## Notes

- Do not run with only `radio_editor.exe` by itself
- `backup/` and `music/` will be created next to the executable
- The app first looks for `ffmpeg.exe` and `fmod tool/` next to the executable
- If not found there, it falls back to `_internal/`

## Release Asset

Recommended upload:

- `FH6_RadioEditor-light-release-2026-05-18.zip`
