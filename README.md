# FH6 Radio Editor

[繁體中文](README.md) | [English](README.en.md)

`FH6 Radio Editor` 是一個給 `ForzaHorizon6` 使用的 Windows GUI 工具，用來編輯 `RadioInfo_*.xml`，並協助處理 FMOD bank 的替換流程。

它把幾件原本分散的工作整合在一起：

- 匯入遊戲內的 `RadioInfo_*.xml`
- 準備、解包、重建 FMOD bank
- 將 `music/` 內的歌曲批次轉成 WAV
- 依序把轉好的 WAV 套到解包後的 sound 檔名
- 在遊戲內確認歌曲對應後，再回來修改 XML 顯示名稱、Artist、長度與 loop
- 額外備份目前修改過的 XML 與 bank，避免遊戲更新覆蓋

## 介面預覽

目前 README 已預留介面預覽區塊。這次變更包含最右側獨立的 `待辦事項` 欄，方便新手照步驟操作。

## 主要功能

- 掃描並載入遊戲中的 `RadioInfo_*.xml`
- 啟動時自動建立：
  - `backup/`
  - `music/`
  - `modified_file/`
- 編輯歌曲欄位：
  - `DisplayName`
  - `Artist`
  - `LengthSeconds`
  - `TrackDrop`
  - `TrackLoopStart`
  - `TrackLoopEnd`
  - `PostDrop`
  - `PostRaceLoopStart`
  - `PostRaceLoopEnd`
- 依音檔自動帶入建議 loop
- 一般播放與 loop 播放預覽
- `Music 轉 WAV`
  - 將 `music/` 內支援格式轉成 `music/converted_wav/*.wav`
  - 自動產生 `music/imported_replacements.txt`
- `一鍵重新命名 WAV`
  - 依 `imported_replacements.txt` 的順序
  - 將轉好的 WAV 複製到 FMOD 解包資料夾
  - 套用原本的 sound 檔名
- 準備、解包、重建、推送 bank
- `備份目前修改檔`
  - 將目前選取的 XML
  - 加上目前勾選的 `.bank`
  - 複製到 `modified_file/`
- 最右側獨立 `待辦事項` 欄

## 使用需求

- Windows
- Python 3.12，或直接使用打包好的 `exe`
- `ForzaHorizon6` 遊戲資料夾
- 另外下載並放在程式同層的工具：
  - `ffmpeg.exe`
  - `fmod tool/Fmod_Bank_Tools.exe`

## 專案結構

開發模式：

```text
FH6_RadioEditor/
|- radio_editor.py
|- radio_editor.spec
|- README.md
|- backup/
|- modified_file/
|- music/
|  |- converted_wav/
|  \- imported_replacements.txt
|- ffmpeg.exe
\- fmod tool/
   |- Fmod_Bank_Tools.exe
   |- bank/
   |- build/
   |- wav/
   \- config.ini
```

發佈版：

```text
radio_editor/
|- radio_editor.exe
|- _internal/
|- ffmpeg.exe
\- fmod tool/
   \- Fmod_Bank_Tools.exe
```

注意：

- 發佈包本身只包含 `radio_editor.exe` 和 `_internal/`
- `ffmpeg.exe` 與 `fmod tool/` 需要另外下載，並放在 `radio_editor.exe` 同層
- 程式第一次啟動時會自動建立 `backup/`、`music/`、`modified_file/`

## 基本流程

1. 選擇遊戲路徑
2. 先選擇要編輯的 XML
3. 選擇要處理的電台
4. 勾選要處理的 bank
5. 按 `準備選取 Bank`
6. 按 `解包選取 Bank`，在 FMOD Bank Tools 內執行 `Extract`
7. 把要替換的歌曲放進 `music/`
8. 按 `Music 轉 WAV`
9. 按 `一鍵重新命名 WAV`
10. 在 FMOD Bank Tools 內執行 `Rebuild`
11. 勾選 `我已手動替換完歌曲`
12. 按 `推送重建好的 Bank`
13. 打開遊戲試聽，確認每首新歌對應到哪個原本歌曲
14. 回到編輯器選擇電台與歌曲
15. 從右側替換清單填入 `DisplayName` / `Artist` / `Length`
16. 需要的話調整 loop，然後按 `套用到歌曲`
17. 按 `儲存 XML`
18. 按 `備份目前修改檔`

## Music 轉 WAV

把歌曲放進 `music/` 後按 `Music 轉 WAV`，程式會：

- 將支援的音訊檔降低 `13dB`
- 輸出到 `music/converted_wav/*.wav`
- 產生 `music/imported_replacements.txt`
- 讓後續 `一鍵重新命名 WAV` 依這份清單順序處理

## 備份說明

程式有兩種備份用途：

- `backup/`
  - 保存原始 XML 與原始 bank
  - 供 `還原 XML`、`還原 Banks` 使用

- `modified_file/`
  - 保存你目前已修改的 XML 與 bank
  - 適合在遊戲更新前先按一次 `備份目前修改檔`
  - 避免更新把你之前修改過的內容覆蓋掉

## 打包

目前使用 PyInstaller 的 `onedir` 模式打包：

```powershell
pyinstaller -y radio_editor.spec
```

輸出位置：

```text
dist/radio_editor/
|- radio_editor.exe
\- _internal/
```

## 注意事項

- 不要只單獨移動 `radio_editor.exe`
- `ffmpeg.exe` 與 `fmod tool/` 必須和 `radio_editor.exe` 放在同一層
- `music/converted_wav/`、`backup/`、`modified_file/` 都屬於執行時資料，不建議提交到版本控制
- bank 重建前，建議先把 XML 與目前修改好的 bank 備份到 `modified_file/`

## License

本專案採用 [MIT License](LICENSE)。
