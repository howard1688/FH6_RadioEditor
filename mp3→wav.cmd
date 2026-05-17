@echo off
:: 設定編碼為 UTF-8，確保中文不會變成亂碼
chcp 65001 >nul

echo ===================================================
echo     開始批次處理：music 資料夾內的音訊轉為 WAV 並降低 13dB
echo ===================================================
echo.
echo 處理中，請耐心等候視窗跑完...
echo.

:: 執行轉檔迴圈 (針對 music 資料夾內的所有音訊，不產生多餘暫存資料夾)
for %%f in (music\*.mp3, music\*.flac, music\*.m4a, music\*.aac, music\*.ogg, music\*.wav) do (
    ffmpeg -y -i "%%f" -af "volume=-13dB" "music\%%~nf_new.wav" && del /q "%%f" && ren "music\%%~nf_new.wav" "%%~nf.wav"
)

echo.
echo ===================================================
echo   轉換完成！music 資料夾裡的音樂已全部處理完畢。
echo ===================================================
echo.

:: 讓視窗停留在畫面上，等待您按任意鍵關閉
pause