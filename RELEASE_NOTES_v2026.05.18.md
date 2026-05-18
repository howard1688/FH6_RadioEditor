# FH6 Radio Editor v2026.05.18

## Highlights

- Added a lightweight release package
- `radio_editor.exe` now works with external `ffmpeg.exe` and `Fmod_Bank_Tools/`
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
- `Fmod_Bank_Tools/`

## Required Extra Downloads

This lightweight release does **not** bundle `ffmpeg.exe` or `Fmod_Bank_Tools/`.

Please download them separately and place them in the same folder as `radio_editor.exe`:

- FFmpeg for Windows:
  - Official download page: https://ffmpeg.org/download.html
  - Windows builds page recommended by FFmpeg: https://www.gyan.dev/ffmpeg/builds/
- FMOD Bank Tools:
  - GitHub project page: https://github.com/Wouldubeinta/Fmod-Bank-Tools

After downloading:

- Place `ffmpeg.exe` next to `radio_editor.exe`
- Place the whole `Fmod_Bank_Tools` folder next to `radio_editor.exe`

## Notes

- Do not run with only `radio_editor.exe` by itself
- `backup/` and `music/` will be created next to the executable
- The app first looks for `ffmpeg.exe` and `Fmod_Bank_Tools/` next to the executable
- If not found there, it falls back to `_internal/`

## Release Asset

Recommended upload:

- `FH6_RadioEditor-light-release-2026-05-18.zip`
