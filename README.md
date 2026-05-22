# FH6 Radio Editor

[繁體中文](README.md) | [English](README.en.md)

`FH6 Radio Editor` 是一個給 `ForzaHorizon6` 使用的 Windows GUI 工具，用來編輯 `RadioInfo_*.xml`，並協助處理 FMOD bank 的替換流程。

這個工具把原本分散的幾件事整合在一起：

- 從遊戲資料夾匯入 XML 與 bank
- 編輯歌曲名稱、Artist、長度與 loop 相關欄位
- 把 `music/` 內的音樂轉成 WAV
- 自動更新 `music/imported_replacements.txt`
- 配合 FMOD Bank Tools 做 Extract / Rebuild
- 在遊戲更新前，額外備份你目前修改過的 XML 與 bank

## 主要功能

- 掃描並載入遊戲中的 `RadioInfo_*.xml`
- 啟動時自動建立 `backup/`、`music/`、`modified_file/`
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
- 播放一般預覽與 loop 預覽
- `Music 轉 WAV`
  - 將 `music/` 內支援格式轉成 `music/converted_wav/*.wav`
  - 自動產生 `music/imported_replacements.txt`
  - 轉換完成後再從 `imported_replacements.txt` 重新載入替換清單
- 準備選取 bank 到 `fmod tool/bank/`
- 開啟 FMOD Bank Tools 做 Extract
- 讀取 Extract 產生的 `*.txt` 清單
- 將重建完成的 bank 推回遊戲資料夾
- 還原 XML 與 bank 備份
- `備份目前修改檔`
  - 將目前選取的 XML
  - 加上目前勾選的 `.bank`
  - 直接備份到 `modified_file/`

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
- 程式啟動後會自動建立 `backup/`、`music/`、`modified_file/`

## 基本使用流程

1. 啟動 `radio_editor.py` 或 `radio_editor.exe`
2. 按 `選擇遊戲路徑`
3. 選擇 `ForzaHorizon6` 根目錄
4. 從上方下拉選單選擇要編輯的 `RadioInfo_*.xml`
5. 選擇歌曲並修改欄位
6. 按 `套用到歌曲`
7. 按 `儲存 XML`

## Music 轉 WAV 流程

如果你要從自己的音樂建立替換清單：

1. 把音樂放進 `music/`
2. 按 `Music 轉 WAV`
3. 程式會自動：
   - 將支援的音訊檔降低 `13dB`
   - 輸出到 `music/converted_wav/*.wav`
   - 產生 `music/imported_replacements.txt`
   - 再從 `imported_replacements.txt` 重新載入替換清單

## FMOD Bank 流程

1. 選擇遊戲路徑
2. 選擇要編輯的 XML
3. 勾選要處理的 bank
4. 按 `準備選取 Bank`
5. 按 `解包選取 Bank`
6. 在 FMOD Bank Tools 內執行 `Extract`
7. 關閉 FMOD Bank Tools
8. 程式會自動讀取對應 `*.txt`
9. 準備好 `music/` 內的替換歌曲
10. 按 `Music 轉 WAV`
11. 手動把轉出的 WAV 套進 FMOD 工具流程
12. 在 FMOD Bank Tools 內執行 `Rebuild`
13. 勾選 `我已手動替換完歌曲`
14. 按 `推送重建好的 Bank`

## 備份說明

程式有兩種備份用途：

- `backup/`
  - 保存原始 XML 與原始 bank
  - 供 `還原 XML`、`還原 Banks` 使用

- `modified_file/`
  - 保存你目前已修改的 XML 與 bank
  - 建議在遊戲更新前按一次 `備份目前修改檔`
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
