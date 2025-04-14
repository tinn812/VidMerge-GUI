import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

class VideoAudioMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("影片與聲音合成工具")

        self.video1 = None
        self.video2 = None
        self.output_file = None

        self.start_time = tk.StringVar(value="00:00:00")
        self.end_time = tk.StringVar(value="99:59:59")
        self.volume = tk.DoubleVar(value=1.0)
        self.output_format = tk.StringVar(value="mp4")
        self.subtitle_file = None


        self.create_widgets()
        self.enable_drag_and_drop()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        self.status_label = ttk.Label(frame, text="拖曳影片/音訊進來", foreground="gray")
        self.status_label.grid(row=0, column=0, columnspan=2)

        ttk.Button(frame, text="選擇來源檔案 1", command=self.select_video1).grid(row=1, column=0, sticky="w")
        ttk.Button(frame, text="選擇來源檔案 2", command=self.select_video2).grid(row=2, column=0, sticky="w")

        ttk.Button(frame, text="選擇字幕檔 (.srt)", command=self.select_subtitle_file).grid(row=9, column=0, sticky="w")
        self.subtitle_label = ttk.Label(frame, text="未選擇字幕")
        self.subtitle_label.grid(row=9, column=1, sticky="w")


        ttk.Label(frame, text="開始時間 (hh:mm:ss)").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.start_time).grid(row=3, column=1)

        ttk.Label(frame, text="結束時間 (hh:mm:ss)").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.end_time).grid(row=4, column=1)

        ttk.Label(frame, text="音量倍率").grid(row=5, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.volume).grid(row=5, column=1)

        ttk.Label(frame, text="輸出格式").grid(row=6, column=0, sticky="w")
        ttk.Combobox(frame, textvariable=self.output_format, values=["mp4", "mkv", "mp3"]).grid(row=6, column=1)

        ttk.Button(frame, text="選擇輸出檔案", command=self.select_output_file).grid(row=7, column=0, sticky="w")

        ttk.Button(frame, text="開始合成", command=self.start_merge).grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame, text="預覽影片片段", command=self.preview_video).grid(row=10, column=0, columnspan=2)


    def enable_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            file = file.strip('"')
            if not self.video1:
                self.video1 = file
                self.status_label.config(text=f"來源 1：{os.path.basename(file)}")
            elif not self.video2:
                self.video2 = file
                self.status_label.config(text=f"來源 1：{os.path.basename(self.video1)}\n來源 2：{os.path.basename(file)}")
            else:
                messagebox.showinfo("提醒", "已選擇兩個檔案，請按『開始合成』")

    def select_video1(self):
        self.video1 = filedialog.askopenfilename(title="選擇影片或音訊 1")

    def select_video2(self):
        self.video2 = filedialog.askopenfilename(title="選擇影片或音訊 2")

    def select_subtitle_file(self):
        file = filedialog.askopenfilename(title="選擇字幕檔案", filetypes=[("Subtitle files", "*.srt")])
        if file:
            self.subtitle_file = file
            self.subtitle_label.config(text=os.path.basename(file))


    def select_output_file(self):
        filetypes = [(f"{self.output_format.get().upper()} files", f"*.{self.output_format.get()}")]
        self.output_file = filedialog.asksaveasfilename(
            title="儲存為", defaultextension=f".{self.output_format.get()}", filetypes=filetypes)
        if not self.output_file:
            self.output_file = os.path.join(os.getcwd(), f"output.{self.output_format.get()}")

    def get_resolution(self, file):
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0", file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            width, height = map(int, result.stdout.strip().split(','))
            return width * height
        except:
            return 0

    def start_merge(self):
        if not self.video1 or not self.video2:
            messagebox.showerror("錯誤", "請選擇兩個來源檔案。")
            return

        if not self.output_file:
            self.output_file = os.path.join(os.getcwd(), f"output.{self.output_format.get()}")

        start_time = self.start_time.get()
        end_time = self.end_time.get()
        volume = self.volume.get()

        # 決定誰是畫面誰是聲音
        video_source = self.video1
        audio_source = self.video2
        if self.video1.lower().endswith(".mp3"):
            audio_source = self.video1
            video_source = self.video2
        elif self.video2.lower().endswith(".mp3"):
            audio_source = self.video2
            video_source = self.video1
        else:
            res1 = self.get_resolution(self.video1)
            res2 = self.get_resolution(self.video2)
            if res2 > res1:
                video_source = self.video2
                audio_source = self.video1

        command = [
            "ffmpeg",
            "-ss", start_time,
            "-to", end_time,
            "-i", audio_source,
            "-ss", start_time,
            "-to", end_time,
            "-i", video_source,
            "-shortest",
            "-c:a", "aac",
            "-filter:a", f"volume={volume}",
        ]

        # 若有字幕就加入字幕 filter，並使用 libx264 編碼影片
        if self.subtitle_file:
            # 處理字幕路徑：改成 ffmpeg 可接受格式
            subtitle_path = self.subtitle_file.replace("\\", "/").replace(":", "\\:")
            command += ["-vf", f"subtitles='{subtitle_path}'", "-c:v", "libx264"]
        else:
            command += ["-c:v", "copy"]


        command.append(self.output_file)


        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("完成", f"合成成功！輸出檔案：{self.output_file}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("錯誤", f"合成失敗：{e}")

    
    def preview_video(self):
        if not self.video1 or not self.video2:
            messagebox.showerror("錯誤", "請先選擇影片與聲音來源")
            return

        start_time = self.start_time.get()
        volume = self.volume.get()

        # 決定聲音與畫面來源
        video_source = self.video2 if self.video1.endswith(".mp3") else self.video1
        audio_source = self.video1 if video_source == self.video2 else self.video2

        # 處理字幕路徑
        subtitle_path = ""
        if self.subtitle_file:
            subtitle_path = self.subtitle_file.replace("\\", "/").replace(":", "\\:")

        # 建立臨時預覽影片檔案
        preview_file = "preview_temp.mp4"

        # 合成指令（5 秒預覽）
        command = [
            "ffmpeg",
            "-y",
            "-ss", start_time,
            "-t", "5",
            "-i", audio_source,
            "-ss", start_time,
            "-t", "5",
            "-i", video_source,
            "-shortest",
            "-filter:a", f"volume={volume}"
        ]

        if subtitle_path:
            command += ["-vf", f"subtitles='{subtitle_path}'", "-c:v", "libx264"]
        else:
            command += ["-c:v", "copy"]

        command += ["-c:a", "aac", preview_file]

        try:
            subprocess.run(command, check=True)
            subprocess.run(["ffplay", "-autoexit", preview_file])
            os.remove(preview_file)
        except Exception as e:
            messagebox.showerror("錯誤", f"預覽失敗：{e}")

