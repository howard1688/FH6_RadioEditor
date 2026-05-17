from __future__ import annotations

import re
import shutil
import configparser
import subprocess
import sys
import tkinter as tk
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def get_app_dir() -> Path:
    entry_path = Path(sys.argv[0]).resolve() if sys.argv and sys.argv[0] else None
    if entry_path is not None:
        return entry_path.parent
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()
INTERNAL_DIR = APP_DIR / "_internal"
SCRIPT_DIR = APP_DIR
BACKUP_DIR = APP_DIR / "backup"
MUSIC_DIR = APP_DIR / "music"
DEFAULT_DIR = BACKUP_DIR if BACKUP_DIR.is_dir() else APP_DIR
DEFAULT_GAME_ROOT = Path(r"D:\SteamLibrary\steamapps\common\ForzaHorizon6")
RADIO_INFO_PATTERN = "RadioInfo_*.xml"
BANK_PATTERN = "R*_Tracks_CU1.assets.bank"
FMOD_TOOL_DIR = APP_DIR / "fmod tool" if (APP_DIR / "fmod tool").is_dir() else INTERNAL_DIR / "fmod tool"
FMOD_TOOL_EXE = FMOD_TOOL_DIR / "Fmod_Bank_Tools.exe"
FMOD_CONFIG_PATH = FMOD_TOOL_DIR / "config.ini"
FMOD_BANK_DIR = FMOD_TOOL_DIR / "bank"
FMOD_BUILD_DIR = FMOD_TOOL_DIR / "build"
DEFAULT_REPLACEMENT_TXT = FMOD_TOOL_DIR / "wav" / "R2_Tracks_CU1.assets[0]" / "R2_Tracks_CU1.assets[0].txt"
FFMPEG_EXE = APP_DIR / "ffmpeg.exe" if (APP_DIR / "ffmpeg.exe").is_file() else INTERNAL_DIR / "ffmpeg.exe"
MUSIC_CONVERT_DIR = MUSIC_DIR / "converted_wav"
MUSIC_REPLACEMENT_TXT = MUSIC_DIR / "imported_replacements.txt"
DISPLAY_DIVISOR = 48000
LOOP_DIVISOR = 44100
FLASH_BUTTON_WIDTH = 26
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
AUDIO_EXTENSIONS = {
    ".aac",
    ".aiff",
    ".alac",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}


def ensure_runtime_dirs() -> None:
    for folder in (BACKUP_DIR, MUSIC_DIR):
        folder.mkdir(parents=True, exist_ok=True)

TEXT = {
    "zh": {},
    "en": {
        "title": "FH6 Radio XML Editor",
        "open": "Select Game Path",
        "save": "Save XML",
        "restore": "Restore",
        "restore_xml": "Restore XML",
        "restore_banks": "Restore Banks",
        "import": "Import from Game",
        "load_replacements": "Load Replacements",
        "deploy": "Deploy",
        "language": "ZH",
        "open_tip": "Select the ForzaHorizon6 root folder; all RadioInfo_*.xml files are backed up and available banks are scanned.",
        "save_tip": "Write current changes directly to the XML inside the ForzaHorizon6 game folder.",
        "restore_tip": "Restore the selected game XML from the copy in this tool's backup folder.",
        "restore_xml_tip": "Restore the currently selected XML from the backup folder.",
        "restore_banks_tip": "Restore the currently checked bank files from the backup folder.",
        "import_tip": "Select the ForzaHorizon6 root folder again and refresh the local backup.",
        "load_replacements_tip": "Load replacement wav names from a txt file or a folder containing wav files.",
        "deploy_tip": "Save the current XML and copy files from fmod tool/build into the game's FMODBanks folder.",
        "language_tip": "Switch the interface language.",
        "apply_tip": "Apply the edited fields to the selected song without saving the file yet.",
        "delete_tip": "Delete the selected song from the current station after confirmation.",
        "delete_unmodified": "Delete Unchanged Names",
        "delete_unmodified_tip": "Delete songs whose DisplayName still matches the backup XML, along with their playlist entries.",
        "stations": "RadioStation",
        "songs": "Songs / Entry Name",
        "song_info": "Song Info",
        "sound_name": "Entry / SoundName",
        "replacement_files": "Replacement File Names",
        "banks": "Bank Selection",
        "prepare_banks": "Prepare Selected Banks",
        "prepare_banks_tip": "Back up only checked banks and copy them into fmod tool/bank.",
        "suggested_banks": "Suggested banks: {banks}",
        "no_suggested_banks": "Suggested banks: none",
        "no_banks_found": "No {pattern} files were found:\n{folder}",
        "no_bank_selected": "Check at least one bank to prepare.",
        "banks_prepared": "Banks prepared: created backups {created_backup}, kept backups {kept_backup}, created tool files {created_tool}, kept tool files {kept_tool}.",
        "use_replacement": "Fill DisplayName",
        "use_replacement_tip": "Fill DisplayName with the selected replacement file name without .wav; Artist is not changed automatically.",
        "replacement_loaded": "Loaded {count} replacement file names.",
        "replacement_empty": "No usable wav file names were found.",
        "replacement_missing": "Default replacement list was not found: {path}. Click Load Replacements to choose one manually.",
        "replacement_no_select": "Please select a replacement file name first.",
        "replacement_applied": "Filled DisplayName from replacement file name: {name}",
        "load_replacement_title": "Load Replacement File Names",
        "fmod_bank_ready": "Prepared original FMOD bank: {path}",
        "fmod_bank_failed": "FMOD bank copy failed",
        "deploy_title": "Deploy",
        "deploy_question": "Save the current XML and copy build files into the game's FMODBanks folder?",
        "deploy_no_game": "Select the ForzaHorizon6 game path first.",
        "deploy_no_build": "Build folder was not found:\n{path}",
        "deploy_empty": "No files were found in the build folder:\n{path}",
        "deploy_done": "Deploy complete: copied {count} files into {path}",
        "deploy_failed": "Deploy failed",
        "length": "Song Length / Seconds",
        "TrackDrop_label": "Race start play point TrackDrop / Time",
        "TrackLoopStart_label": "Race loop return point TrackLoopStart / Time",
        "TrackLoopEnd_label": "Race loop end point TrackLoopEnd / Time",
        "PostDrop_label": "Post-race play point PostDrop / Time",
        "PostRaceLoopStart_label": "Post-race loop return point PostRaceLoopStart / Time",
        "PostRaceLoopEnd_label": "Post-race loop end point PostRaceLoopEnd / Time",
        "TrackDrop_help": "When the game shows Start, playback begins from this timestamp.",
        "TrackLoopStart_help": "Race loop return timestamp; playback jumps here when TrackLoopEnd is reached.",
        "TrackLoopEnd_help": "Race loop end timestamp; playback jumps back to TrackLoopStart when reached.",
        "PostDrop_help": "After the finish animation and result message, playback begins from this timestamp.",
        "PostRaceLoopStart_help": "Post-race loop return timestamp; playback jumps here when PostRaceLoopEnd is reached.",
        "PostRaceLoopEnd_help": "Post-race loop end timestamp; playback jumps back to PostRaceLoopStart when reached.",
        "apply": "Apply to Song",
        "delete": "Delete",
        "ready": "Ready",
        "song_count": "{count} songs",
        "select_game_root": "Select ForzaHorizon6 Root Folder",
        "copy_prompt": "Click Select Game Path first, then choose the ForzaHorizon6 root folder.",
        "copy_done": "Checked backup: created {created} new backups, kept {kept} existing backups. Now choose the language XML to edit.",
        "copy_missing": "Missing required files:\n{files}",
        "no_radio_info": "No RadioInfo_*.xml files were found:\n{folder}",
        "copy_failed": "Copy failed",
        "open_xml": "Open Radio XML",
        "xml_parse": "XML parse error",
        "open_failed": "Open failed",
        "loaded": "Loaded {path} ({count} stations)",
        "choose_xml": "Choose the language XML to edit from the XML dropdown.",
        "selected": "Selected {name}: {count} songs",
        "no_matching_sample": "{name} has Entry but no matching Sample",
        "no_song_title": "No song",
        "no_song_sample": "Please select a song with Sample data first.",
        "no_song": "Please select a song first.",
        "format_conflict": "Format conflict",
        "time_required": "{label} cannot be empty.",
        "time_invalid": "{label} must be seconds or M:SS.mmm time, such as 68.720 or 1:08.720.",
        "time_negative": "{label} cannot be negative.",
        "applied": "Applied changes to {name}. Click Save to write XML.",
        "confirm_delete": "Confirm delete",
        "delete_question": "Delete {name} from this station?",
        "deleted": "Deleted {name} ({count} playlist entries removed). Click Save to write XML.",
        "save_failed": "Save failed",
        "saved_title": "Saved",
        "saved": "Saved directly to the game XML.\nLocal backup: {backup}",
        "saved_status": "Saved to game folder: {path}",
        "no_backup": "No backup",
        "no_backup_found": "No backup found:\n{path}",
        "restore_backup": "Restore backup",
        "restore_question": "Restore from {backup}? Current file will be replaced.",
        "restore_failed": "Restore failed",
        "restored": "Restored {name} from {backup}",
        "convert_music": "Convert Music",
        "convert_music_tip": "Lower every supported file in the music folder by 13dB, convert to wav, and rebuild the pending replacement queue.",
        "replacement_queue": "Pending replacements: {pending} / {total}",
        "replacement_assigned": "Assigned {name}. Pending replacement queue: {pending} left.",
        "music_ffmpeg_missing": "ffmpeg.exe was not found:\n{path}",
        "music_no_files": "No supported audio files were found in the music folder.",
        "music_convert_failed": "Audio conversion failed",
        "music_convert_done": "Converted {count} songs into {folder} and refreshed the replacement queue:\n{txt}",
        "replacement_waiting": "Waiting for the next batch: {count}",
        "replacement_slots": "Available for this station now: {available} / {slots} slots",
        "extract_banks": "Extract Selected Banks",
        "extract_banks_tip": "Open FMOD Bank Tools with the selected banks prepared. After you finish Extract and close the tool, matching txt lists will be loaded automatically.",
        "extract_no_tool": "Fmod_Bank_Tools.exe was not found:\n{path}",
        "extract_no_txt": "No extracted txt list was found for the selected bank yet. Use Extract in FMOD Bank Tools, then close it.",
        "extract_loaded": "Loaded extracted replacement names from {count} bank txt list(s).",
        "manual_replace_done": "I finished manual song replacement",
        "manual_replace_done_tip": "Enable rebuild only after you have manually replaced the extracted wav files with your target songs.",
        "rebuild_bank": "Push Built Banks",
        "rebuild_bank_tip": "After you rebuild inside FMOD Bank Tools and close it, copy the built bank files back into the game folder.",
        "rebuild_not_ready": "Please confirm manual song replacement is finished before rebuild.",
        "rebuild_no_files": "No rebuilt bank files were found for the selected bank names in:\n{path}",
        "rebuild_done": "Copied {count} rebuilt bank file(s) into {path}",
        "extract_running": "FMOD Bank Tools is open. Use Extract there; this editor will load the txt list after the tool closes.",
        "rebuild_running": "FMOD Bank Tools is open for rebuild.",
        "restore_bank_question": "Restore the checked bank files from backup?",
        "restore_bank_missing": "No backup was found for:\n{files}",
        "restore_bank_done": "Restored {count} bank file(s) into {path}",
        "delete_unmodified_none": "No songs in this station still use the backup DisplayName.",
        "delete_unmodified_question": "Delete every song in this station whose DisplayName still matches the backup XML?",
        "delete_unmodified_done": "Deleted {songs} unchanged-name song(s) and removed {entries} playlist entry/entries.",
    },
}

ZH_TEXT = {
    "title": "FH6 電台 XML 編輯器",
    "open": "選擇遊戲路徑",
    "save": "儲存 XML",
    "restore_xml": "還原 XML",
    "restore_banks": "還原 Banks",
    "load_replacements": "載入替換清單",
    "language": "English",
    "open_tip": "選擇 ForzaHorizon6 根目錄，程式會備份 RadioInfo XML 並掃描可用的 bank。",
    "save_tip": "只把目前 XML 編輯結果寫回遊戲資料夾。",
    "restore_xml_tip": "用 backup 裡對應的 XML 還原目前選中的 XML。",
    "restore_banks_tip": "用 backup 裡對應的 bank 還原目前勾選的 bank。",
    "load_replacements_tip": "從 txt 或 wav 資料夾載入替換檔名。",
    "language_tip": "切換介面語言。",
    "apply_tip": "把目前右側欄位套用到選中的歌曲，但尚未存檔。",
    "delete_tip": "刪除目前歌曲，會同時移除這個電台所有 PlayList 裡對應的 Entry。",
    "delete_unmodified": "刪除未改名歌曲",
    "delete_unmodified_tip": "一鍵刪除目前電台中 DisplayName 與 backup 相同的歌曲與 PlayList Entry。",
    "stations": "電台",
    "songs": "歌曲 / Entry Name",
    "song_info": "歌曲資訊",
    "sound_name": "Entry / SoundName",
    "replacement_files": "替換檔名",
    "banks": "Bank 選擇",
    "prepare_banks": "準備選取 Bank",
    "prepare_banks_tip": "把勾選的 bank 複製到 backup 與 fmod tool/bank。",
    "suggested_banks": "建議 Bank：{banks}",
    "no_suggested_banks": "建議 Bank：無",
    "no_banks_found": "找不到 {pattern}：\n{folder}",
    "no_bank_selected": "請先勾選 bank。",
    "banks_prepared": "Bank 準備完成：新增備份 {created_backup}、保留備份 {kept_backup}、新增工具檔 {created_tool}、保留工具檔 {kept_tool}。",
    "use_replacement": "填入 DisplayName",
    "use_replacement_tip": "把選取的檔名去掉 .wav 後填入 DisplayName；Artist 不會自動修改。",
    "replacement_loaded": "已載入 {count} 個替換檔名。",
    "replacement_empty": "沒有可用的 wav 檔名。",
    "replacement_missing": "找不到預設替換清單：{path}",
    "replacement_no_select": "請先選取替換檔名。",
    "replacement_applied": "已把替換檔名填入 DisplayName：{name}",
    "load_replacement_title": "載入替換檔名",
    "fmod_bank_failed": "FMOD bank 複製失敗",
    "length": "歌曲長度 / 秒",
    "TrackDrop_label": "起跑播放點 TrackDrop / 時間",
    "TrackLoopStart_label": "比賽循環起點 TrackLoopStart / 時間",
    "TrackLoopEnd_label": "比賽循環終點 TrackLoopEnd / 時間",
    "PostDrop_label": "賽後播放點 PostDrop / 時間",
    "PostRaceLoopStart_label": "賽後循環起點 PostRaceLoopStart / 時間",
    "PostRaceLoopEnd_label": "賽後循環終點 PostRaceLoopEnd / 時間",
    "TrackDrop_help": "比賽開始時，歌曲會從這個時間點開始播放。",
    "TrackLoopStart_help": "比賽進入循環後，會從這個時間點重新開始播放。",
    "TrackLoopEnd_help": "比賽循環播放到這個時間點時，會跳回 TrackLoopStart。",
    "PostDrop_help": "比賽結束進入賽後畫面時，歌曲會從這個時間點開始播放。",
    "PostRaceLoopStart_help": "賽後循環段落會從這個時間點重新開始播放。",
    "PostRaceLoopEnd_help": "賽後循環播放到這個時間點時，會跳回 PostRaceLoopStart。",
    "apply": "套用到歌曲",
    "delete": "刪除歌曲",
    "ready": "就緒",
    "song_count": "{count} 首歌",
    "select_game_root": "選擇 ForzaHorizon6 根目錄",
    "copy_prompt": "先按「選擇遊戲路徑」，再選擇 ForzaHorizon6 根目錄。",
    "copy_done": "備份完成：新增 {created} 份、保留 {kept} 份。接著請選擇要編輯的 XML。",
    "copy_missing": "缺少必要檔案：\n{files}",
    "no_radio_info": "找不到 RadioInfo_*.xml：\n{folder}",
    "copy_failed": "複製失敗",
    "open_xml": "開啟 XML",
    "xml_parse": "XML 解析失敗",
    "open_failed": "開啟失敗",
    "loaded": "已載入 {path}（{count} 個電台）",
    "choose_xml": "請從上方 XML 下拉選單選擇要編輯的語言檔。",
    "selected": "已選擇 {name}：{count} 首歌",
    "no_matching_sample": "{name} 有 Entry 但找不到對應 Sample",
    "no_song_title": "未選擇歌曲",
    "no_song_sample": "請先選擇含有 Sample 資料的歌曲。",
    "no_song": "請先選擇歌曲。",
    "format_conflict": "格式錯誤",
    "time_required": "{label} 不能空白。",
    "time_invalid": "{label} 必須是秒數或 M:SS.mmm，例如 68.720 或 1:08.720。",
    "time_negative": "{label} 不能是負數。",
    "applied": "已套用 {name}，記得按「儲存 XML」。",
    "confirm_delete": "確認刪除",
    "delete_question": "要從目前電台刪除 {name} 嗎？",
    "deleted": "已刪除 {name}，共移除 {count} 個 playlist entry。記得按「儲存 XML」。",
    "save_failed": "儲存失敗",
    "saved_title": "已儲存",
    "saved": "已儲存 XML。\n本地備份：{backup}",
    "saved_status": "已儲存到遊戲資料夾：{path}",
    "no_backup": "找不到備份",
    "no_backup_found": "找不到備份：\n{path}",
    "restore_backup": "還原備份",
    "restore_question": "要從 {backup} 還原嗎？目前檔案會被覆蓋。",
    "restore_failed": "還原失敗",
    "restored": "已從 {backup} 還原 {name}",
    "convert_music": "Music 轉 WAV",
    "convert_music_tip": "把 music 裡的音樂降低 13dB 並轉成 wav，然後更新待替換清單。",
    "replacement_queue": "待替換：{pending} / 總共 {total}",
    "replacement_assigned": "已套用 {name}，待替換剩 {pending} 首。",
    "music_ffmpeg_missing": "找不到 ffmpeg.exe：\n{path}",
    "music_no_files": "music 資料夾裡沒有可轉換的音訊檔。",
    "music_convert_failed": "音訊轉換失敗",
    "music_convert_done": "已轉換 {count} 首到 {folder}，並更新待替換清單：\n{txt}",
    "replacement_waiting": "下一輪待處理：{count}",
    "replacement_slots": "目前電台可替換：{available} / {slots}",
    "extract_banks": "解包選取 Bank",
    "extract_banks_tip": "準備好選取的 bank 並開啟 FMOD Bank Tools。完成 Extract 並關閉後，會自動讀取對應 txt 清單。",
    "extract_no_tool": "找不到 Fmod_Bank_Tools.exe：\n{path}",
    "extract_no_txt": "找不到解包後的 txt 清單。請先在 FMOD Bank Tools 裡按 Extract，再關閉工具。",
    "extract_loaded": "已載入 {count} 個 bank 的解包 txt 清單。",
    "manual_replace_done": "我已手動替換完歌曲",
    "manual_replace_done_tip": "只有在你手動覆蓋完解包出的 wav 後，才啟用推送 bank。",
    "rebuild_bank": "推送重建好的 Bank",
    "rebuild_bank_tip": "把 fmod tool/build 裡已經重建好的 bank 複製回遊戲資料夾。",
    "rebuild_not_ready": "請先確認已完成手動替換歌曲。",
    "rebuild_no_files": "在下列資料夾找不到對應的重建 bank：\n{path}",
    "rebuild_done": "已把 {count} 個重建 bank 複製到 {path}",
    "extract_running": "FMOD Bank Tools 已開啟。請在那邊按 Extract，關閉後本工具會自動讀取 txt 清單。",
    "rebuild_running": "FMOD Bank Tools 已開啟，可在那邊進行 Rebuild。",
    "restore_bank_question": "要用 backup 裡的 bank 還原目前勾選的 bank 嗎？",
    "restore_bank_missing": "以下 bank 找不到備份：\n{files}",
    "restore_bank_done": "已還原 {count} 個 bank 到 {path}",
    "delete_unmodified_none": "目前電台沒有 DisplayName 與 backup 相同的歌曲。",
    "delete_unmodified_question": "要一鍵刪除目前電台中所有未改過 DisplayName 的歌曲嗎？",
    "delete_unmodified_done": "已刪除 {songs} 首未改名歌曲，共移除 {entries} 個 playlist entry。",
}


def get_text(lang: str, key: str) -> str:
    if lang == "zh":
        return ZH_TEXT.get(key, TEXT["en"][key])
    return TEXT["en"][key]


@dataclass
class SongRef:
    sound_name: str
    sample: ET.Element | None


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str = "") -> None:
        self.widget = widget
        self.text = text
        self.tip_window: tk.Toplevel | None = None
        self.after_id: str | None = None
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def set_text(self, text: str) -> None:
        self.text = text
        if self.tip_window is not None:
            self.hide()

    def schedule(self, _event: tk.Event | None = None) -> None:
        self.cancel()
        self.after_id = self.widget.after(450, self.show)

    def cancel(self) -> None:
        if self.after_id is not None:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def show(self) -> None:
        self.after_id = None
        if not self.text or self.tip_window is not None:
            return

        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tip_window,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5,
            wraplength=360,
        )
        label.pack()

    def hide(self, _event: tk.Event | None = None) -> None:
        self.cancel()
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None


class RadioEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("FH6 Radio XML Editor")
        self.geometry("1320x840")
        self.minsize(1120, 720)

        self.xml_path: Path | None = None
        self.tree: ET.ElementTree | None = None
        self.root_node: ET.Element | None = None
        self.stations: list[ET.Element] = []
        self.songs: list[SongRef] = []
        self.current_station: ET.Element | None = None
        self.current_song: SongRef | None = None
        self.game_root: Path | None = None
        self.game_audio_dir: Path | None = None
        self.game_bank_dir: Path | None = None
        self.available_banks: list[Path] = []
        self.bank_vars: dict[Path, tk.BooleanVar] = {}
        self.suggested_bank_names: set[str] = set()
        self.replacement_names: list[str] = []
        self.waiting_replacement_names: list[str] = []
        self.replacement_catalog: list[str] = []
        self.assigned_replacements: dict[str, str] = {}
        self.song_replacement_candidates: dict[str, str] = {}
        self.fields: dict[str, tk.StringVar] = {}
        self.lang = "zh"
        self.labels: dict[str, ttk.Label] = {}
        self.buttons: dict[str, ttk.Button] = {}
        self.frames: dict[str, ttk.LabelFrame] = {}
        self.tooltips: dict[str, Tooltip] = {}
        self.label_tooltips: dict[str, Tooltip] = {}
        self.flash_after_id: str | None = None
        self.replacement_flash_after_id: str | None = None
        self.replacement_flash_on = False
        self.flash_on = False
        self.manual_replace_done_var = tk.BooleanVar(value=False)
        self.fmod_process: subprocess.Popen[str] | None = None
        self.fmod_after_id: str | None = None
        self.pending_fmod_action: str | None = None
        self.pending_fmod_banks: list[Path] = []
        self.marker_fields = [
            ("TrackDrop", DISPLAY_DIVISOR),
            ("PostDrop", DISPLAY_DIVISOR),
            ("TrackLoopStart", LOOP_DIVISOR),
            ("TrackLoopEnd", LOOP_DIVISOR),
            ("PostRaceLoopStart", LOOP_DIVISOR),
            ("PostRaceLoopEnd", LOOP_DIVISOR),
        ]

        self._build_ui()
        self.apply_language()
        self.load_default_replacements()
        if self.replacement_names:
            self.status_var.set(self.t("copy_prompt"))
        self.start_game_path_flash()

    def t(self, key: str, **kwargs: object) -> str:
        value = get_text(self.lang, key)
        return value.format(**kwargs) if kwargs else value

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=10)
        top.grid(row=0, column=0, columnspan=3, sticky="ew")
        top.columnconfigure(1, weight=1)

        self.labels["xml"] = ttk.Label(top, text="XML")
        self.labels["xml"].grid(row=0, column=0, padx=(0, 8))
        self.xml_combo = ttk.Combobox(top, state="readonly", width=82)
        self.xml_combo.grid(row=0, column=1, sticky="ew")
        self.xml_combo.bind("<<ComboboxSelected>>", lambda _event: self.load_xml(Path(self.xml_combo.get())))
        self.buttons["open"] = ttk.Button(top, command=self.import_game_files_from_dialog)
        self.buttons["open"].grid(row=0, column=2, padx=6)
        self.buttons["save"] = ttk.Button(top, command=self.save_xml)
        self.buttons["save"].grid(row=0, column=3, padx=6)
        self.buttons["restore_xml"] = ttk.Button(top, command=self.restore_xml_backup)
        self.buttons["restore_xml"].grid(row=0, column=4, padx=6)
        self.buttons["restore_banks"] = ttk.Button(top, command=self.restore_selected_banks)
        self.buttons["restore_banks"].grid(row=0, column=5, padx=6)
        self.buttons["load_replacements"] = ttk.Button(top, command=self.load_replacements_dialog)
        self.buttons["load_replacements"].grid(row=0, column=6, padx=6)
        self.buttons["language"] = ttk.Button(top, command=self.toggle_language)
        self.buttons["language"].grid(row=0, column=7)

        station_frame = ttk.LabelFrame(self, padding=8)
        self.frames["stations"] = station_frame
        station_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        station_frame.rowconfigure(0, weight=1)
        self.station_list = tk.Listbox(station_frame, width=36, exportselection=False)
        self.station_list.grid(row=0, column=0, sticky="nsew")
        station_scroll = ttk.Scrollbar(station_frame, command=self.station_list.yview)
        station_scroll.grid(row=0, column=1, sticky="ns")
        self.station_list.configure(yscrollcommand=station_scroll.set)
        self.station_list.bind("<<ListboxSelect>>", self.on_station_selected)

        bank_frame = ttk.LabelFrame(station_frame, padding=8)
        self.frames["banks"] = bank_frame
        bank_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        bank_frame.columnconfigure(0, weight=1)
        self.bank_checks_frame = ttk.Frame(bank_frame)
        self.bank_checks_frame.grid(row=0, column=0, sticky="ew")
        self.suggested_banks_var = tk.StringVar(value="")
        ttk.Label(bank_frame, textvariable=self.suggested_banks_var, wraplength=320, justify="left").grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.buttons["prepare_banks"] = ttk.Button(bank_frame, command=self.prepare_selected_banks)
        self.buttons["prepare_banks"].grid(row=2, column=0, sticky="e", pady=(8, 0))
        self.buttons["extract_banks"] = ttk.Button(bank_frame, command=self.extract_selected_banks)
        self.buttons["extract_banks"].grid(row=3, column=0, sticky="e", pady=(8, 0))
        self.manual_replace_done_check = ttk.Checkbutton(
            bank_frame,
            variable=self.manual_replace_done_var,
            command=self.update_rebuild_button_state,
        )
        self.manual_replace_done_check.grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.buttons["rebuild_bank"] = ttk.Button(bank_frame, command=self.rebuild_selected_banks, state="disabled")
        self.buttons["rebuild_bank"].grid(row=5, column=0, sticky="e", pady=(8, 0))

        song_frame = ttk.LabelFrame(self, padding=8)
        self.frames["songs"] = song_frame
        song_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))
        song_frame.rowconfigure(1, weight=1)
        song_frame.columnconfigure(0, weight=1)
        self.song_count = ttk.Label(song_frame, text="")
        self.song_count.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.song_list = tk.Listbox(song_frame, width=50, exportselection=False)
        self.song_list.grid(row=1, column=0, sticky="nsew")
        song_scroll = ttk.Scrollbar(song_frame, command=self.song_list.yview)
        song_scroll.grid(row=1, column=1, sticky="ns")
        self.song_list.configure(yscrollcommand=song_scroll.set)
        self.song_list.bind("<<ListboxSelect>>", self.on_song_selected)

        info = ttk.LabelFrame(self, padding=12)
        self.frames["song_info"] = info
        info.grid(row=1, column=2, sticky="nsew", padx=(5, 10), pady=(0, 10))
        info.columnconfigure(1, weight=1)

        self.sound_name_var = tk.StringVar(value="")
        self.labels["sound_name"] = ttk.Label(info)
        self.labels["sound_name"].grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(info, textvariable=self.sound_name_var, state="readonly").grid(row=0, column=1, sticky="ew", pady=4)

        self._add_field(info, "DisplayName", "DisplayName", 1)
        self._add_field(info, "Artist", "Artist", 2)
        self._add_field(info, "LengthSeconds", "", 3)

        row = 4
        for name, divisor in self.marker_fields:
            label = f"{name} / {divisor}"
            self._add_field(info, name, label, row)
            self.label_tooltips[name] = Tooltip(self.labels[name])
            row += 1

        button_row = ttk.Frame(info)
        button_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        button_row.columnconfigure(0, weight=1)
        self.buttons["apply"] = ttk.Button(button_row, command=self.apply_song_changes)
        self.buttons["apply"].grid(row=0, column=1, padx=6)
        self.buttons["delete"] = ttk.Button(button_row, command=self.delete_song)
        self.buttons["delete"].grid(row=0, column=2)
        self.buttons["delete_unmodified"] = ttk.Button(button_row, command=self.delete_unmodified_songs)
        self.buttons["delete_unmodified"].grid(row=0, column=3, padx=(6, 0))

        replacement_frame = ttk.LabelFrame(info, padding=8)
        self.frames["replacement_files"] = replacement_frame
        replacement_frame.grid(row=row + 1, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        replacement_frame.columnconfigure(0, weight=1)
        replacement_frame.rowconfigure(0, weight=1)
        self.replacement_list = tk.Listbox(replacement_frame, height=8, exportselection=False)
        self.replacement_list.grid(row=0, column=0, sticky="nsew")
        replacement_scroll = ttk.Scrollbar(replacement_frame, command=self.replacement_list.yview)
        replacement_scroll.grid(row=0, column=1, sticky="ns")
        self.replacement_list.configure(yscrollcommand=replacement_scroll.set)
        self.replacement_list.bind("<Double-Button-1>", lambda _event: self.use_selected_replacement())
        self.replacement_info_var = tk.StringVar(value="")
        ttk.Label(replacement_frame, textvariable=self.replacement_info_var, anchor="w").grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.waiting_info_var = tk.StringVar(value="")
        ttk.Label(replacement_frame, textvariable=self.waiting_info_var, anchor="w").grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.waiting_replacement_list = tk.Listbox(replacement_frame, height=5, exportselection=False)
        self.waiting_replacement_list.grid(row=3, column=0, sticky="nsew")
        waiting_scroll = ttk.Scrollbar(replacement_frame, command=self.waiting_replacement_list.yview)
        waiting_scroll.grid(row=3, column=1, sticky="ns")
        self.waiting_replacement_list.configure(yscrollcommand=waiting_scroll.set)
        replacement_buttons = ttk.Frame(replacement_frame)
        replacement_buttons.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        replacement_buttons.columnconfigure(0, weight=1)
        self.buttons["convert_music"] = ttk.Button(replacement_buttons, command=self.convert_music_folder)
        self.buttons["convert_music"].grid(row=0, column=0, sticky="w")
        self.buttons["use_replacement"] = ttk.Button(replacement_buttons, command=self.use_selected_replacement)
        self.buttons["use_replacement"].grid(row=0, column=1, sticky="e", padx=(8, 0))
        self._setup_button_tooltips()

        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, anchor="w").grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 8))

    def _setup_button_tooltips(self) -> None:
        for key in ("open", "save", "restore_xml", "restore_banks", "load_replacements", "language", "prepare_banks", "extract_banks", "rebuild_bank", "apply", "delete", "delete_unmodified", "use_replacement", "convert_music"):
            self.tooltips[key] = Tooltip(self.buttons[key])
        self.tooltips["manual_replace_done"] = Tooltip(self.manual_replace_done_check)

    def _add_field(self, parent: ttk.Frame, key: str, label: str, row: int) -> None:
        var = tk.StringVar(value="")
        self.fields[key] = var
        self.labels[key] = ttk.Label(parent, text=label)
        self.labels[key].grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=4)

    def apply_language(self) -> None:
        self.title(self.t("title"))
        for key in ("open", "save", "restore_xml", "restore_banks", "load_replacements", "language", "prepare_banks", "extract_banks", "rebuild_bank", "apply", "delete", "delete_unmodified", "use_replacement", "convert_music"):
            self.buttons[key].configure(text=self.t(key))
            self.tooltips[key].set_text(self.t(f"{key}_tip"))
        self.buttons["language"].configure(text="English" if self.lang == "zh" else "ZH")
        self.manual_replace_done_check.configure(text=self.t("manual_replace_done"))
        self.tooltips["manual_replace_done"].set_text(self.t("manual_replace_done_tip"))

        self.frames["stations"].configure(text=self.t("stations"))
        self.frames["banks"].configure(text=self.t("banks"))
        self.frames["songs"].configure(text=self.t("songs"))
        self.frames["song_info"].configure(text=self.t("song_info"))
        self.frames["replacement_files"].configure(text=self.t("replacement_files"))
        self.labels["sound_name"].configure(text=self.t("sound_name"))
        self.labels["LengthSeconds"].configure(text=self.t("length"))
        self.labels["DisplayName"].configure(text="DisplayName")
        self.labels["Artist"].configure(text="Artist")
        for marker_name, divisor in self.marker_fields:
            self.labels[marker_name].configure(text=f"{self.t(f'{marker_name}_label')} (/{divisor})")
            self.label_tooltips[marker_name].set_text(self.t(f"{marker_name}_help"))
        self.song_count.configure(text=self.t("song_count", count=len(self.songs)))
        self.update_suggested_banks_label()
        self.update_replacement_info()
        if not self.status_var.get():
            self.status_var.set(self.t("ready"))
        if self.game_root is None:
            self.start_game_path_flash()

    def toggle_language(self) -> None:
        self.lang = "en" if self.lang == "zh" else "zh"
        self.apply_language()

    def _load_xml_choices(self) -> None:
        if self.game_audio_dir is None:
            self.xml_combo["values"] = []
            self.xml_combo.set("")
            return

        paths = sorted(self.game_audio_dir.glob(RADIO_INFO_PATTERN))
        self.xml_combo["values"] = [str(path) for path in paths]
        self.xml_combo.set("")
        self.station_list.delete(0, tk.END)
        self.song_list.delete(0, tk.END)
        self.clear_song_info()
        self.status_var.set(self.t("choose_xml"))

    def scan_game_banks(self) -> None:
        if self.game_bank_dir is None:
            self.available_banks = []
        else:
            self.available_banks = sorted(self.game_bank_dir.glob(BANK_PATTERN))

        for child in self.bank_checks_frame.winfo_children():
            child.destroy()
        self.bank_vars.clear()

        for row, bank_path in enumerate(self.available_banks):
            var = tk.BooleanVar(value=False)
            self.bank_vars[bank_path] = var
            ttk.Checkbutton(
                self.bank_checks_frame,
                text=bank_path.name,
                variable=var,
                command=self.update_rebuild_button_state,
            ).grid(row=row, column=0, sticky="w")

        self.update_suggested_banks_label()
        self.update_rebuild_button_state()
        if self.game_bank_dir is not None and not self.available_banks:
            self.status_var.set(self.t("no_banks_found", pattern=BANK_PATTERN, folder=self.game_bank_dir))

    def selected_bank_paths(self) -> list[Path]:
        return [path for path, var in self.bank_vars.items() if var.get()]

    def update_rebuild_button_state(self) -> None:
        selected_banks = self.selected_bank_paths()
        enabled = bool(selected_banks) and self.manual_replace_done_var.get()
        if "rebuild_bank" in self.buttons:
            self.buttons["rebuild_bank"].configure(state="normal" if enabled else "disabled")

    def reset_rebuild_confirmation(self) -> None:
        self.manual_replace_done_var.set(False)
        self.update_rebuild_button_state()

    def set_fmod_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for key in ("prepare_banks", "extract_banks", "rebuild_bank"):
            if key in self.buttons:
                self.buttons[key].configure(state=state)
        self.manual_replace_done_check.configure(state=state)

    def start_fmod_tool(self, action: str, banks: list[Path]) -> bool:
        if self.fmod_process is not None:
            return False

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self.fmod_process = subprocess.Popen(
                [str(FMOD_TOOL_EXE)],
                cwd=str(FMOD_TOOL_DIR),
                creationflags=creationflags,
            )
        except OSError as exc:
            messagebox.showerror(self.t(action), str(exc))
            return False

        self.pending_fmod_action = action
        self.pending_fmod_banks = list(banks)
        self.set_fmod_buttons_enabled(False)
        self.status_var.set(self.t("extract_running" if action == "extract_banks" else "rebuild_running"))
        self.poll_fmod_tool()
        return True

    def poll_fmod_tool(self) -> None:
        if self.fmod_process is None:
            return
        if self.fmod_process.poll() is None:
            self.fmod_after_id = self.after(800, self.poll_fmod_tool)
            return

        action = self.pending_fmod_action
        banks = list(self.pending_fmod_banks)
        self.fmod_process = None
        self.pending_fmod_action = None
        self.pending_fmod_banks = []
        self.fmod_after_id = None
        self.set_fmod_buttons_enabled(True)
        self.update_rebuild_button_state()

        if action == "extract_banks":
            self.load_extracted_replacement_texts(banks)

    def update_suggested_banks_label(self) -> None:
        if not hasattr(self, "suggested_banks_var"):
            return
        if self.suggested_bank_names:
            banks = ", ".join(sorted(self.suggested_bank_names))
            self.suggested_banks_var.set(self.t("suggested_banks", banks=banks))
        else:
            self.suggested_banks_var.set(self.t("no_suggested_banks"))

    def start_game_path_flash(self) -> None:
        if self.game_root is not None or self.flash_after_id is not None:
            return
        self.flash_game_path_button()

    def stop_game_path_flash(self) -> None:
        if self.flash_after_id is not None:
            self.after_cancel(self.flash_after_id)
            self.flash_after_id = None
        self.flash_on = False
        self.buttons["open"].configure(text=self.t("open"), width=0)

    def flash_game_path_button(self) -> None:
        if self.game_root is not None:
            self.stop_game_path_flash()
            return
        self.flash_on = not self.flash_on
        text = f">>> {self.t('open')} <<<" if self.flash_on else self.t("open")
        self.buttons["open"].configure(text=text, width=FLASH_BUTTON_WIDTH)
        self.flash_after_id = self.after(650, self.flash_game_path_button)

    def start_replacement_flash(self) -> None:
        if self.replacement_names or self.replacement_flash_after_id is not None:
            return
        self.flash_replacement_button()

    def stop_replacement_flash(self) -> None:
        if self.replacement_flash_after_id is not None:
            self.after_cancel(self.replacement_flash_after_id)
            self.replacement_flash_after_id = None
        self.replacement_flash_on = False
        self.buttons["load_replacements"].configure(text=self.t("load_replacements"), width=0)

    def flash_replacement_button(self) -> None:
        if self.replacement_names:
            self.stop_replacement_flash()
            return
        self.replacement_flash_on = not self.replacement_flash_on
        text = f">>> {self.t('load_replacements')} <<<" if self.replacement_flash_on else self.t("load_replacements")
        self.buttons["load_replacements"].configure(text=text, width=FLASH_BUTTON_WIDTH)
        self.replacement_flash_after_id = self.after(700, self.flash_replacement_button)

    def import_game_files_from_dialog(self, show_cancel: bool = True) -> bool:
        initial_dir = DEFAULT_GAME_ROOT if DEFAULT_GAME_ROOT.exists() else SCRIPT_DIR
        folder = filedialog.askdirectory(
            title=self.t("select_game_root"),
            initialdir=str(initial_dir),
            mustexist=True,
        )
        if not folder:
            if show_cancel:
                self.status_var.set(self.t("copy_prompt"))
            return False
        return self.import_game_files(Path(folder))

    def import_game_files(self, game_root: Path) -> bool:
        audio_dir = game_root / "media" / "Audio"
        radio_info_paths = sorted(audio_dir.glob(RADIO_INFO_PATTERN))
        if not radio_info_paths:
            messagebox.showerror(self.t("copy_failed"), self.t("no_radio_info", folder=audio_dir))
            return False

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        created = 0
        kept = 0
        try:
            for source in radio_info_paths:
                backup_xml = BACKUP_DIR / source.name
                if backup_xml.exists():
                    kept += 1
                else:
                    shutil.copy2(source, backup_xml)
                    created += 1
        except OSError as exc:
            messagebox.showerror(self.t("copy_failed"), str(exc))
            return False

        self.game_root = game_root
        self.game_audio_dir = audio_dir
        self.game_bank_dir = audio_dir / "FMODBanks"
        self.stop_game_path_flash()
        self.status_var.set(self.t("copy_done", created=created, kept=kept))
        self.scan_game_banks()
        self._load_xml_choices()
        return True

    def prepare_fmod_bank_copy(self, backup_bank: Path) -> None:
        try:
            FMOD_BANK_DIR.mkdir(parents=True, exist_ok=True)
            target = FMOD_BANK_DIR / backup_bank.name
            if not target.exists():
                shutil.copy2(backup_bank, target)
        except OSError as exc:
            messagebox.showerror(self.t("fmod_bank_failed"), str(exc))

    def prepare_selected_banks(self) -> None:
        selected_banks = self.selected_bank_paths()
        if not selected_banks:
            messagebox.showwarning(self.t("banks"), self.t("no_bank_selected"))
            return

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        FMOD_BANK_DIR.mkdir(parents=True, exist_ok=True)
        created_backup = 0
        kept_backup = 0
        created_tool = 0
        kept_tool = 0

        try:
            for source in selected_banks:
                backup_target = BACKUP_DIR / source.name
                if backup_target.exists():
                    kept_backup += 1
                else:
                    shutil.copy2(source, backup_target)
                    created_backup += 1

                tool_target = FMOD_BANK_DIR / source.name
                if tool_target.exists():
                    kept_tool += 1
                else:
                    shutil.copy2(backup_target, tool_target)
                    created_tool += 1
        except OSError as exc:
            messagebox.showerror(self.t("fmod_bank_failed"), str(exc))
            return

        self.status_var.set(
            self.t(
                "banks_prepared",
                created_backup=created_backup,
                kept_backup=kept_backup,
                created_tool=created_tool,
                kept_tool=kept_tool,
            )
        )

    def write_fmod_config(self) -> None:
        config = configparser.ConfigParser()
        config.optionxform = str
        if FMOD_CONFIG_PATH.is_file():
            config.read(FMOD_CONFIG_PATH, encoding="utf-8")

        if not config.has_section("Directorys"):
            config.add_section("Directorys")
        if not config.has_section("Options"):
            config.add_section("Options")

        config["Directorys"]["BankDir"] = FMOD_BANK_DIR.resolve().as_posix()
        config["Directorys"]["WavDir"] = (FMOD_TOOL_DIR / "wav").resolve().as_posix()
        config["Directorys"]["RebuildDir"] = FMOD_BUILD_DIR.resolve().as_posix()
        config["Directorys"]["CacheDir"] = (FMOD_TOOL_DIR / "fsbcache").resolve().as_posix()

        with FMOD_CONFIG_PATH.open("w", encoding="utf-8") as config_file:
            config.write(config_file)

    @staticmethod
    def extracted_txt_path_for_bank(bank_path: Path) -> Path:
        folder_name = f"{bank_path.stem}[0]"
        return FMOD_TOOL_DIR / "wav" / folder_name / f"{folder_name}.txt"

    def load_extracted_replacement_texts(self, banks: list[Path]) -> bool:
        extracted_names: list[str] = []
        found_paths = 0
        for bank in banks:
            txt_path = self.extracted_txt_path_for_bank(bank)
            if not txt_path.is_file():
                continue
            extracted_names.extend(self.read_replacement_text(txt_path))
            found_paths += 1

        if not extracted_names:
            messagebox.showwarning(self.t("extract_banks"), self.t("extract_no_txt"))
            return False

        self.set_replacement_names(extracted_names, show_status=False)
        self.status_var.set(self.t("extract_loaded", count=found_paths))
        return True

    def extract_selected_banks(self) -> None:
        selected_banks = self.selected_bank_paths()
        if not selected_banks:
            messagebox.showwarning(self.t("banks"), self.t("no_bank_selected"))
            return
        if not FMOD_TOOL_EXE.is_file():
            messagebox.showerror(self.t("extract_banks"), self.t("extract_no_tool", path=FMOD_TOOL_EXE))
            return

        self.prepare_selected_banks()
        self.reset_rebuild_confirmation()
        self.write_fmod_config()
        self.start_fmod_tool("extract_banks", selected_banks)

    def rebuild_selected_banks(self) -> None:
        selected_banks = self.selected_bank_paths()
        if not selected_banks:
            messagebox.showwarning(self.t("banks"), self.t("no_bank_selected"))
            return
        if not self.manual_replace_done_var.get():
            messagebox.showwarning(self.t("rebuild_bank"), self.t("rebuild_not_ready"))
            return
        if self.game_bank_dir is None:
            messagebox.showwarning(self.t("rebuild_bank"), self.t("deploy_no_game"))
            return
        if not FMOD_BUILD_DIR.is_dir():
            messagebox.showwarning(self.t("rebuild_bank"), self.t("deploy_no_build", path=FMOD_BUILD_DIR))
            return

        selected_names = {bank.name for bank in selected_banks}
        built_files = [path for path in FMOD_BUILD_DIR.rglob("*") if path.is_file() and path.name in selected_names]
        if not built_files:
            messagebox.showwarning(self.t("rebuild_bank"), self.t("rebuild_no_files", path=FMOD_BUILD_DIR))
            return

        try:
            self.game_bank_dir.mkdir(parents=True, exist_ok=True)
            copied = 0
            for source in built_files:
                target = self.game_bank_dir / source.name
                shutil.copy2(source, target)
                copied += 1
        except OSError as exc:
            messagebox.showerror(self.t("rebuild_bank"), str(exc))
            return

        self.status_var.set(self.t("rebuild_done", count=copied, path=self.game_bank_dir))

    def load_replacements_dialog(self) -> None:
        file_name = filedialog.askopenfilename(
            title=self.t("load_replacement_title"),
            initialdir=str(DEFAULT_REPLACEMENT_TXT.parent if DEFAULT_REPLACEMENT_TXT.parent.exists() else SCRIPT_DIR),
            filetypes=[("Text or wav files", "*.txt *.wav"), ("Text files", "*.txt"), ("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if not file_name:
            folder_name = filedialog.askdirectory(title=self.t("load_replacement_title"), initialdir=str(SCRIPT_DIR), mustexist=True)
            if not folder_name:
                return
            names = [path.stem for path in sorted(Path(folder_name).glob("*.wav"))]
        else:
            path = Path(file_name)
            if path.suffix.lower() == ".wav":
                names = [wav_path.stem for wav_path in sorted(path.parent.glob("*.wav"))]
            else:
                names = self.read_replacement_text(path)

        self.set_replacement_names(names)

    def load_default_replacements(self) -> None:
        if DEFAULT_REPLACEMENT_TXT.is_file():
            names = self.read_replacement_text(DEFAULT_REPLACEMENT_TXT)
            self.set_replacement_names(names, show_status=False)
            if not names:
                self.status_var.set(self.t("replacement_empty"))
                self.start_replacement_flash()
        else:
            self.status_var.set(self.t("replacement_missing", path=DEFAULT_REPLACEMENT_TXT))
            self.start_replacement_flash()

    @staticmethod
    def dedupe_preserve_order(names: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            deduped.append(name)
        return deduped

    def set_replacement_names(self, names: list[str], show_status: bool = True) -> None:
        self.replacement_catalog = self.dedupe_preserve_order(names)
        self.refresh_replacement_list()

        if show_status:
            if self.replacement_catalog:
                self.status_var.set(self.t("replacement_loaded", count=len(self.replacement_catalog)))
            else:
                self.status_var.set(self.t("replacement_empty"))
        if self.replacement_catalog:
            self.stop_replacement_flash()
        else:
            self.start_replacement_flash()

    def refresh_replacement_list(self) -> None:
        assigned = set(self.assigned_replacements.values())
        unassigned_names = [name for name in self.replacement_catalog if name not in assigned]
        capacity = self.current_station_capacity()
        assigned_count = self.current_station_assigned_count()

        if capacity > 0:
            visible_capacity = max(0, capacity - assigned_count)
            self.replacement_names = unassigned_names[:visible_capacity]
            self.waiting_replacement_names = unassigned_names[visible_capacity:]
        else:
            self.replacement_names = unassigned_names
            self.waiting_replacement_names = []

        self.replacement_list.delete(0, tk.END)
        for name in self.replacement_names:
            self.replacement_list.insert(tk.END, name)
        self.waiting_replacement_list.delete(0, tk.END)
        for name in self.waiting_replacement_names:
            self.waiting_replacement_list.insert(tk.END, name)
        self.update_replacement_info()

    def current_station_capacity(self) -> int:
        return len(self.songs) if self.current_station is not None else 0

    def current_station_assigned_count(self) -> int:
        if self.current_station is None:
            return 0
        current_sound_names = {song.sound_name for song in self.songs}
        return sum(1 for sound_name in self.assigned_replacements if sound_name in current_sound_names)

    def update_replacement_info(self) -> None:
        if hasattr(self, "replacement_info_var"):
            slots = self.current_station_capacity()
            if slots > 0:
                self.replacement_info_var.set(
                    self.t("replacement_slots", available=len(self.replacement_names), slots=slots)
                )
            else:
                self.replacement_info_var.set(
                    self.t("replacement_queue", pending=len(self.replacement_names), total=len(self.replacement_catalog))
                )
        if hasattr(self, "waiting_info_var"):
            self.waiting_info_var.set(self.t("replacement_waiting", count=len(self.waiting_replacement_names)))

    @staticmethod
    def iter_music_sources() -> list[Path]:
        sources: list[Path] = []
        for path in sorted(MUSIC_DIR.rglob("*")):
            if not path.is_file():
                continue
            if path.is_relative_to(MUSIC_CONVERT_DIR):
                continue
            if path.suffix.lower() not in AUDIO_EXTENSIONS:
                continue
            sources.append(path)
        return sources

    @staticmethod
    def unique_wav_target(target_dir: Path, stem: str) -> Path:
        candidate = target_dir / f"{stem}.wav"
        index = 2
        while candidate.exists():
            candidate = target_dir / f"{stem} ({index}).wav"
            index += 1
        return candidate

    def convert_music_folder(self) -> None:
        if not FFMPEG_EXE.is_file():
            messagebox.showerror(self.t("music_convert_failed"), self.t("music_ffmpeg_missing", path=FFMPEG_EXE))
            return

        ensure_runtime_dirs()
        music_sources = self.iter_music_sources()
        if not music_sources:
            messagebox.showwarning(self.t("music_convert_failed"), self.t("music_no_files"))
            return

        MUSIC_CONVERT_DIR.mkdir(parents=True, exist_ok=True)
        for existing in MUSIC_CONVERT_DIR.glob("*.wav"):
            existing.unlink(missing_ok=True)

        converted_names: list[str] = []
        errors: list[str] = []
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        for source in music_sources:
            target = self.unique_wav_target(MUSIC_CONVERT_DIR, source.stem)
            command = [
                str(FFMPEG_EXE),
                "-y",
                "-i",
                str(source),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-af",
                "volume=-13dB",
                str(target),
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=creationflags,
                check=False,
            )
            if result.returncode != 0:
                errors.append(f"{source.name}: {result.stderr.strip() or result.stdout.strip() or result.returncode}")
                continue
            converted_names.append(target.stem)

        if not converted_names:
            messagebox.showerror(self.t("music_convert_failed"), "\n\n".join(errors[:3]) if errors else self.t("music_no_files"))
            return

        MUSIC_REPLACEMENT_TXT.write_text(
            "\n".join(f"{name}.wav" for name in converted_names),
            encoding="utf-8",
        )
        self.set_replacement_names(converted_names, show_status=False)

        status = self.t(
            "music_convert_done",
            count=len(converted_names),
            folder=MUSIC_CONVERT_DIR,
            txt=MUSIC_REPLACEMENT_TXT,
        )
        if errors:
            status = f"{status}\n\n{errors[0]}"
        self.status_var.set(status)

    @staticmethod
    def read_replacement_text(path: Path) -> list[str]:
        names: list[str] = []
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="mbcs").splitlines()

        for line in lines:
            text = line.strip().strip('"')
            if not text:
                continue
            if text.lower().endswith(".wav"):
                text = Path(text).stem
            names.append(text)
        return names

    def use_selected_replacement(self) -> None:
        if not self.current_song:
            messagebox.showwarning(self.t("no_song_title"), self.t("no_song"))
            return

        selection = self.replacement_list.curselection()
        if not selection:
            messagebox.showwarning(self.t("replacement_files"), self.t("replacement_no_select"))
            return

        replacement_name = self.replacement_names[selection[0]]
        self.fields["DisplayName"].set(replacement_name)
        self.song_replacement_candidates[self.current_song.sound_name] = replacement_name
        self.status_var.set(self.t("replacement_applied", name=replacement_name))

    def commit_replacement_assignment(self, sound_name: str) -> None:
        candidate = self.song_replacement_candidates.pop(sound_name, None)
        if not candidate:
            return

        self.assigned_replacements[sound_name] = candidate
        self.refresh_replacement_list()
        self.status_var.set(self.t("replacement_assigned", name=candidate, pending=len(self.replacement_names)))

    def deploy_build_files(self) -> None:
        if self.game_root is None:
            messagebox.showwarning(self.t("deploy_title"), self.t("deploy_no_game"))
            return
        if not FMOD_BUILD_DIR.is_dir():
            messagebox.showwarning(self.t("deploy_title"), self.t("deploy_no_build", path=FMOD_BUILD_DIR))
            return

        build_files = [path for path in FMOD_BUILD_DIR.rglob("*") if path.is_file()]
        if not build_files:
            messagebox.showwarning(self.t("deploy_title"), self.t("deploy_empty", path=FMOD_BUILD_DIR))
            return

        if not messagebox.askyesno(self.t("deploy_title"), self.t("deploy_question")):
            return

        if self.tree is not None and self.xml_path is not None:
            if not self.write_current_xml(show_message=False):
                return

        target_dir = self.game_root / "media" / "Audio" / "FMODBanks"
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            copied = 0
            for source in build_files:
                relative = source.relative_to(FMOD_BUILD_DIR)
                target = target_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                copied += 1
        except OSError as exc:
            messagebox.showerror(self.t("deploy_failed"), str(exc))
            return

        self.status_var.set(self.t("deploy_done", count=copied, path=target_dir))
        messagebox.showinfo(self.t("deploy_title"), self.t("deploy_done", count=copied, path=target_dir))

    def open_xml(self) -> None:
        file_name = filedialog.askopenfilename(
            title=self.t("open_xml"),
            initialdir=str(BACKUP_DIR if BACKUP_DIR.is_dir() else SCRIPT_DIR),
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if file_name:
            self.load_xml(Path(file_name))

    def load_xml(self, path: Path) -> None:
        try:
            self.tree = ET.parse(path)
        except ET.ParseError as exc:
            messagebox.showerror(self.t("xml_parse"), str(exc))
            return
        except OSError as exc:
            messagebox.showerror(self.t("open_failed"), str(exc))
            return

        self.xml_path = path
        self.root_node = self.tree.getroot()
        self.stations = list(self.root_node.findall(".//RadioStation"))
        self.station_list.delete(0, tk.END)
        self.song_list.delete(0, tk.END)
        self.clear_song_info()

        for station in self.stations:
            name = station.get("Name", "(no name)")
            number = station.get("Number", "?")
            self.station_list.insert(tk.END, f"{number} - {name}")

        self.status_var.set(self.t("loaded", path=path, count=len(self.stations)))

    def on_station_selected(self, _event: tk.Event) -> None:
        selection = self.station_list.curselection()
        if not selection:
            return
        self.current_station = self.stations[selection[0]]
        self.current_song = None
        self.clear_song_info()
        self.update_station_bank_suggestions(self.current_station)
        self.load_station_songs(self.current_station)
        self.refresh_replacement_list()

    def update_station_bank_suggestions(self, station: ET.Element) -> None:
        self.suggested_bank_names = set()
        for bank in station.findall("./Banks/Bank"):
            name = bank.get("Name", "")
            if name.endswith("_Tracks_CU1"):
                self.suggested_bank_names.add(f"{name}.assets.bank")

        for bank_path, var in self.bank_vars.items():
            var.set(bank_path.name in self.suggested_bank_names)
        self.update_suggested_banks_label()

    def load_station_songs(self, station: ET.Element) -> None:
        sample_map: dict[str, ET.Element] = {}
        track_list = station.find("./SampleList[@Type='Track']")
        if track_list is not None:
            for sample in track_list.findall("./Sample"):
                sound_name = sample.get("SoundName")
                if sound_name:
                    sample_map[sound_name] = sample

        ordered_names: list[str] = []
        for playlist in station.findall("./PlayList"):
            for entry in playlist.findall("./Entry"):
                name = entry.get("Name")
                if name and name in sample_map and name not in ordered_names:
                    ordered_names.append(name)

        if not ordered_names:
            ordered_names = list(sample_map.keys())

        self.songs = [SongRef(name, sample_map.get(name)) for name in ordered_names]
        self.song_list.delete(0, tk.END)
        for song in self.songs:
            self.song_list.insert(tk.END, song.sound_name)

        station_name = station.get("Name", "(no name)")
        self.song_count.configure(text=self.t("song_count", count=len(self.songs)))
        self.status_var.set(self.t("selected", name=station_name, count=len(self.songs)))
        self.update_replacement_info()

    def on_song_selected(self, _event: tk.Event) -> None:
        selection = self.song_list.curselection()
        if not selection:
            return
        self.current_song = self.songs[selection[0]]
        self.show_song_info(self.current_song)

    def show_song_info(self, song: SongRef) -> None:
        self.clear_song_info()
        self.sound_name_var.set(song.sound_name)
        sample = song.sample
        if sample is None:
            self.status_var.set(self.t("no_matching_sample", name=song.sound_name))
            return

        self.fields["DisplayName"].set(sample.get("DisplayName", ""))
        self.fields["Artist"].set(sample.get("Artist", ""))
        self.fields["LengthSeconds"].set(self.format_seconds(sample.get("SampleLength"), DISPLAY_DIVISOR))

        for marker_name, divisor in self.marker_fields:
            marker = self.find_marker(sample, marker_name)
            self.fields[marker_name].set(self.format_seconds(marker.get("Position") if marker is not None else None, divisor))

    def clear_song_info(self) -> None:
        self.sound_name_var.set("")
        for var in self.fields.values():
            var.set("")

    def apply_song_changes(self) -> None:
        if not self.current_song or self.current_song.sample is None:
            messagebox.showwarning(self.t("no_song_title"), self.t("no_song_sample"))
            return

        sample = self.current_song.sample
        try:
            display_name = self.clean_text(self.fields["DisplayName"].get(), "DisplayName")
            artist = self.clean_text(self.fields["Artist"].get(), "Artist")
            length_pos = self.parse_seconds(self.fields["LengthSeconds"].get(), DISPLAY_DIVISOR, self.t("length"), self.lang)
            marker_positions = {
                name: self.parse_seconds(self.fields[name].get(), divisor, self.t(f"{name}_label"), self.lang)
                for name, divisor in self.marker_fields
                if self.fields[name].get().strip()
            }
            self.validate_positions(length_pos, marker_positions)
        except ValueError as exc:
            messagebox.showerror(self.t("format_conflict"), str(exc))
            return

        sample.set("DisplayName", display_name)
        sample.set("Artist", artist)
        sample.set("SampleLength", str(length_pos))

        end_marker = self.ensure_marker(sample, "End")
        end_marker.set("Position", str(max(0, length_pos - 1)))

        for marker_name, position in marker_positions.items():
            self.ensure_marker(sample, marker_name).set("Position", str(position))

        had_candidate = self.current_song.sound_name in self.song_replacement_candidates
        self.show_song_info(self.current_song)
        self.commit_replacement_assignment(self.current_song.sound_name)
        if not had_candidate:
            self.status_var.set(self.t("applied", name=self.current_song.sound_name))

    def delete_song(self) -> None:
        if not self.current_station or not self.current_song:
            messagebox.showwarning(self.t("no_song_title"), self.t("no_song"))
            return

        song_name = self.current_song.sound_name
        if not messagebox.askyesno(self.t("confirm_delete"), self.t("delete_question", name=song_name)):
            return

        removed_entries = self.remove_songs_from_current_station({song_name})
        self.load_station_songs(self.current_station)
        self.clear_song_info()
        self.status_var.set(self.t("deleted", name=song_name, count=removed_entries))

    def remove_songs_from_current_station(self, song_names: set[str]) -> int:
        if not self.current_station:
            return 0

        track_list = self.current_station.find("./SampleList[@Type='Track']")
        if track_list is not None:
            for sample in list(track_list.findall("./Sample")):
                sound_name = sample.get("SoundName")
                if sound_name in song_names:
                    track_list.remove(sample)

        removed_entries = 0
        for playlist in self.current_station.findall("./PlayList"):
            for entry in list(playlist.findall("./Entry")):
                if entry.get("Name") in song_names:
                    playlist.remove(entry)
                    removed_entries += 1

        for song_name in song_names:
            self.song_replacement_candidates.pop(song_name, None)
            self.assigned_replacements.pop(song_name, None)
        self.refresh_replacement_list()
        return removed_entries

    def current_backup_display_map(self) -> dict[str, str]:
        if self.xml_path is None:
            return {}
        backup_path = self.backup_path_for(self.xml_path)
        if not backup_path.is_file():
            return {}

        try:
            backup_tree = ET.parse(backup_path)
        except (ET.ParseError, OSError):
            return {}

        backup_root = backup_tree.getroot()
        station_name = self.current_station.get("Name") if self.current_station is not None else None
        station_number = self.current_station.get("Number") if self.current_station is not None else None
        if station_name is None or station_number is None:
            return {}

        for station in backup_root.findall(".//RadioStation"):
            if station.get("Name") == station_name and station.get("Number") == station_number:
                track_list = station.find("./SampleList[@Type='Track']")
                if track_list is None:
                    return {}
                return {
                    sample.get("SoundName", ""): sample.get("DisplayName", "")
                    for sample in track_list.findall("./Sample")
                    if sample.get("SoundName")
                }
        return {}

    def delete_unmodified_songs(self) -> None:
        if not self.current_station:
            messagebox.showwarning(self.t("no_song_title"), self.t("no_song"))
            return

        backup_display_map = self.current_backup_display_map()
        unmodified_names = {
            song.sound_name
            for song in self.songs
            if song.sample is not None
            and song.sound_name in backup_display_map
            and song.sample.get("DisplayName", "") == backup_display_map[song.sound_name]
        }

        if not unmodified_names:
            messagebox.showinfo(self.t("delete_unmodified"), self.t("delete_unmodified_none"))
            return
        if not messagebox.askyesno(self.t("delete_unmodified"), self.t("delete_unmodified_question")):
            return

        removed_entries = self.remove_songs_from_current_station(unmodified_names)
        removed_song_count = len(unmodified_names)
        self.load_station_songs(self.current_station)
        self.clear_song_info()
        self.status_var.set(self.t("delete_unmodified_done", songs=removed_song_count, entries=removed_entries))

    def save_xml(self) -> None:
        self.write_current_xml(show_message=True)

    def write_current_xml(self, show_message: bool) -> bool:
        if not self.tree or not self.xml_path:
            return False
        backup_path = self.backup_path_for(self.xml_path)
        try:
            if not backup_path.exists() and self.xml_path.exists():
                BACKUP_DIR.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.xml_path, backup_path)
            ET.indent(self.tree, space="  ")
            self.tree.write(self.xml_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
        except OSError as exc:
            messagebox.showerror(self.t("save_failed"), str(exc))
            return False
        self.status_var.set(self.t("saved_status", path=self.xml_path, backup=backup_path.name))
        if show_message:
            messagebox.showinfo(self.t("saved_title"), self.t("saved", backup=backup_path))
        return True

    def restore_xml_backup(self) -> None:
        if not self.xml_path:
            return
        backup_path = self.backup_path_for(self.xml_path)
        if not backup_path.exists():
            messagebox.showwarning(self.t("no_backup"), self.t("no_backup_found", path=backup_path))
            return
        if not messagebox.askyesno(self.t("restore_backup"), self.t("restore_question", backup=backup_path.name)):
            return
        try:
            shutil.copy2(backup_path, self.xml_path)
        except OSError as exc:
            messagebox.showerror(self.t("restore_failed"), str(exc))
            return
        self.load_xml(self.xml_path)
        self.status_var.set(self.t("restored", name=self.xml_path.name, backup=backup_path.name))

    def restore_selected_banks(self) -> None:
        selected_banks = self.selected_bank_paths()
        if not selected_banks:
            messagebox.showwarning(self.t("banks"), self.t("no_bank_selected"))
            return
        if self.game_bank_dir is None:
            messagebox.showwarning(self.t("restore_banks"), self.t("deploy_no_game"))
            return

        missing = [bank.name for bank in selected_banks if not self.backup_path_for(bank).is_file()]
        if missing:
            messagebox.showwarning(self.t("restore_banks"), self.t("restore_bank_missing", files="\n".join(missing)))
            return
        if not messagebox.askyesno(self.t("restore_banks"), self.t("restore_bank_question")):
            return

        try:
            self.game_bank_dir.mkdir(parents=True, exist_ok=True)
            restored = 0
            for bank in selected_banks:
                backup_bank = self.backup_path_for(bank)
                shutil.copy2(backup_bank, self.game_bank_dir / bank.name)
                restored += 1
        except OSError as exc:
            messagebox.showerror(self.t("restore_banks"), str(exc))
            return

        self.status_var.set(self.t("restore_bank_done", count=restored, path=self.game_bank_dir))

    @staticmethod
    def backup_path_for(path: Path) -> Path:
        return BACKUP_DIR / path.name

    @staticmethod
    def find_marker(sample: ET.Element, name: str) -> ET.Element | None:
        for marker in sample.findall("./Marker"):
            if marker.get("Name") == name:
                return marker
        return None

    def ensure_marker(self, sample: ET.Element, name: str) -> ET.Element:
        marker = self.find_marker(sample, name)
        if marker is None:
            marker = ET.SubElement(sample, "Marker")
            marker.set("Name", name)
            marker.set("Position", "-1")
        return marker

    @staticmethod
    def format_seconds(raw_value: str | None, divisor: int) -> str:
        if raw_value is None or raw_value == "":
            return ""
        try:
            value = int(raw_value)
        except ValueError:
            return ""
        if value < 0:
            return ""
        total_seconds = value / divisor
        minutes = int(total_seconds // 60)
        seconds = total_seconds - minutes * 60
        return f"{minutes}:{seconds:06.3f}"

    @staticmethod
    def parse_seconds(raw_value: str, divisor: int, label: str, lang: str) -> int:
        text = raw_value.strip()
        if not text:
            raise ValueError(get_text(lang, "time_required").format(label=label))
        try:
            if ":" in text:
                minute_text, second_text = text.split(":", 1)
                value = int(minute_text.strip()) * 60 + float(second_text.strip())
            else:
                value = float(text)
        except ValueError as exc:
            raise ValueError(get_text(lang, "time_invalid").format(label=label)) from exc
        if value < 0:
            raise ValueError(get_text(lang, "time_negative").format(label=label))
        return int(round(value * divisor))

    @staticmethod
    def clean_text(raw_value: str, label: str) -> str:
        value = raw_value.strip()
        if not value:
            raise ValueError(f"{label} cannot be empty.")
        if CONTROL_CHARS.search(value):
            raise ValueError(f"{label} contains invalid XML control characters.")
        return value

    @staticmethod
    def validate_positions(length: int, positions: dict[str, int]) -> None:
        for name, position in positions.items():
            if position >= length:
                raise ValueError(f"{name} must be smaller than song length.")

        ordered_pairs = [
            ("TrackLoopStart", "TrackLoopEnd"),
            ("PostRaceLoopStart", "PostRaceLoopEnd"),
        ]
        for start_name, end_name in ordered_pairs:
            if start_name in positions and end_name in positions:
                if positions[start_name] >= positions[end_name]:
                    raise ValueError(f"{start_name} must be smaller than {end_name}.")


if __name__ == "__main__":
    ensure_runtime_dirs()
    app = RadioEditor()
    app.mainloop()
