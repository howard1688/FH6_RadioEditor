# FH6 Radio Editor

[中文](README.md) | [English](README.en.md)

`FH6 Radio Editor` is a Windows GUI tool for `ForzaHorizon6` focused on editing `RadioInfo_*.xml` and helping with FMOD bank replacement.

This project is built around a practical workflow:

- back up original XML and `.bank` files
- edit song display names, artists, and playback markers
- extract selected banks
- lower imported songs by `13dB` and convert them to WAV
- rebuild banks with FMOD Bank Tools
- push rebuilt `.bank` files back into the game folder

## Features

- `RadioInfo_*.xml` browser and editor
- automatic creation of `backup/` and `music/`
- automatic backup of game XML files
- station list and song list view
- edit:
  - `DisplayName`
  - `Artist`
  - `SampleLength`
  - `TrackDrop`
  - `TrackLoopStart`
  - `TrackLoopEnd`
  - `PostDrop`
  - `PostRaceLoopStart`
  - `PostRaceLoopEnd`
- delete the current song from the current station
- delete every song whose `DisplayName` still matches the backup XML
- suggested bank hints based on the selected station
- prepare selected banks into `backup/` and `Fmod_Bank_Tools/bank/` (legacy `fmod tool/` is also supported)
- launch FMOD Bank Tools for extraction
- auto-load extracted `*.txt` replacement lists after FMOD Bank Tools closes
- convert audio in `music/` to WAV with `-13dB` gain
- build a replacement queue from imported songs
- restore XML from backup
- restore selected banks from backup
- push rebuilt banks from `Fmod_Bank_Tools/build/` back to the game folder
- Traditional Chinese / English UI

## Folder Layout

```text
FH6_RadioEditor/
|- radio_editor.py
|- backup/
|- music/
|  |- converted_wav/
|  \- imported_replacements.txt
\- Fmod_Bank_Tools/
   |- Fmod_Bank_Tools.exe
   |- bank/
   |- wav/
   |- build/
   \- config.ini
```

## Requirements

- Windows
- Python 3.12 recommended for running `radio_editor.py`
- A valid `ForzaHorizon6` installation
- For full functionality, provide these files alongside the app:
  - `ffmpeg.exe`
  - `Fmod_Bank_Tools/Fmod_Bank_Tools.exe`

## Quick Start

1. Run:

   ```powershell
   python radio_editor.py
   ```

2. Click `Select Game Path`
3. Choose your `ForzaHorizon6` root folder
4. Select one `RadioInfo_*.xml` file from the XML dropdown
5. Pick a station and song
6. Edit `DisplayName`, `Artist`, or playback markers
7. Click `Save XML` to write the XML back to the game folder

## FMOD Bank Workflow

The bank workflow is intentionally semi-manual for stability.

1. Select the game path
2. Choose an XML and station
3. Check the bank file(s) you want to work on
4. Click `Prepare Selected Banks`
5. Click `Extract Selected Banks`
6. FMOD Bank Tools opens
7. Use `Extract` inside FMOD Bank Tools
8. Close FMOD Bank Tools
9. The editor auto-loads the extracted `*.txt` list
10. Put your source songs into `music/`
11. Click `Convert Music`
12. Replace the extracted WAV files manually inside `Fmod_Bank_Tools/wav/...`
13. Rebuild inside FMOD Bank Tools
14. Close FMOD Bank Tools
15. Check `I finished manual song replacement`
16. Click `Push Built Banks`

## Replacement Queue

After you import songs into `music/` and click `Convert Music`, the tool creates:

- `music/converted_wav/`
- `music/imported_replacements.txt`

This list is used as a `DisplayName` replacement source.

If you import more songs than the current station should handle at once, the UI splits them into:

- replacements available for this station now
- songs waiting for the next batch

Once a replacement name is successfully applied, it is removed from the active queue.

## Restore Actions

The top bar separates restore actions into:

- `Restore XML`
- `Restore Banks`

`Restore XML` restores the currently selected XML only.  
`Restore Banks` restores only the checked bank files.

## Song Deletion Behavior

Deleting a song removes more than a visible list row.

The tool also removes:

- the matching `Sample` in the current station
- matching `<Entry Name="...">` nodes in that station's playlist sections

`Delete Unchanged Names` removes songs whose `DisplayName` still matches the backup XML, along with their playlist entries.

## Release Build Notes

If you use the packaged `exe` release, keep the whole folder together instead of using only `radio_editor.exe`.

The lightweight release package should include:

- `radio_editor.exe`
- `_internal/`

Users should also place these next to the `exe`:

- `ffmpeg.exe`
- `Fmod_Bank_Tools/` (legacy `fmod tool/` is also supported)

At runtime, the app first looks next to the `exe` for:

- `ffmpeg.exe`
- `Fmod_Bank_Tools/`

If they are not there, it falls back to `_internal/`.

The app also:

- creates `backup/` and `music/` next to the `exe`
- keeps `backup/` and `music/` as user data folders

## Notes

- Keep backups before editing files
- Replacement audio should stay compatible with the source bank expectations
- In general, replacement audio should be the same length as or shorter than the original
- After replacing bank audio, it is still a good idea to verify in-game which new song maps to which XML entry before finalizing `DisplayName` and `Artist`

## Credits

- FMOD Bank Tools: used here for bank extraction and rebuild convenience. See [fmod tool/README.md](fmod%20tool/README.md)
- `ffmpeg.exe`: used for audio conversion and gain adjustment

## License

This repository currently does not include a formal license file.  
If you plan to publish it broadly, adding a `LICENSE` file would be a good next step.
