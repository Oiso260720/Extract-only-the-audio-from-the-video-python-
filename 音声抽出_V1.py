from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import imageio_ffmpeg


def run_ffmpeg(cmd):
    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def extract_audio():
    video = filedialog.askopenfilename(
        title="動画を選択",
        filetypes=[
            ("動画", "*.mp4 *.mov *.avi *.mkv *.wmv *.m4v"),
            ("すべて", "*.*")
        ]
    )

    if not video:
        return

    video_path = Path(video)
    output_dir = filedialog.askdirectory(title="出力フォルダを選択")

    if not output_dir:
        return

    output_dir = Path(output_dir)

    mode = mode_var.get()
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    try:
        if mode == "all":
            output = output_dir / f"{video_path.stem}.mp3"

            cmd = [
                ffmpeg_exe,
                "-y",
                "-i", str(video_path),
                "-vn",
                "-codec:a", "libmp3lame",
                "-q:a", "2",
                str(output)
            ]

            run_ffmpeg(cmd)

            messagebox.showinfo("完了", f"保存先:\n{output}")

        else:
            try:
                segment_minutes = float(segment_entry.get())
            except ValueError:
                messagebox.showerror("エラー", "分割時間は数値で入力してください。")
                return

            if segment_minutes <= 0:
                messagebox.showerror("エラー", "分割時間は0より大きい値にしてください。")
                return

            segment_seconds = int(segment_minutes * 60)

            output_pattern = output_dir / f"{video_path.stem}_%03d.mp3"

            cmd = [
                ffmpeg_exe,
                "-y",
                "-i", str(video_path),
                "-vn",
                "-codec:a", "libmp3lame",
                "-q:a", "2",
                "-f", "segment",
                "-segment_time", str(segment_seconds),
                "-reset_timestamps", "1",
                str(output_pattern)
            ]

            run_ffmpeg(cmd)

            messagebox.showinfo(
                "完了",
                f"分割MP3を書き出しました。\n保存先:\n{output_dir}"
            )

    except subprocess.CalledProcessError:
        messagebox.showerror(
            "エラー",
            "ffmpegで変換に失敗しました。動画に音声トラックがない可能性があります。"
        )
    except Exception as e:
        messagebox.showerror("エラー", str(e))


def update_segment_state():
    if mode_var.get() == "split":
        segment_entry.config(state="normal")
    else:
        segment_entry.config(state="disabled")


root = tk.Tk()
root.title("動画からMP3音声を抽出")

mode_var = tk.StringVar(value="all")

tk.Label(root, text="出力方法").grid(row=0, column=0, padx=10, pady=10, sticky="w")

tk.Radiobutton(
    root,
    text="全体を1つのMP3にする",
    variable=mode_var,
    value="all",
    command=update_segment_state
).grid(row=1, column=0, padx=20, pady=5, sticky="w")

tk.Radiobutton(
    root,
    text="指定時間ごとに分割する",
    variable=mode_var,
    value="split",
    command=update_segment_state
).grid(row=2, column=0, padx=20, pady=5, sticky="w")

tk.Label(root, text="分割時間（分）").grid(row=3, column=0, padx=10, pady=10, sticky="w")

segment_entry = tk.Entry(root, width=10)
segment_entry.insert(0, "30")
segment_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

tk.Button(
    root,
    text="動画を選択して実行",
    command=extract_audio,
    width=25
).grid(row=4, column=0, columnspan=2, padx=10, pady=20)

update_segment_state()

root.mainloop()