import os
import sys
import threading
import platform
import contextlib
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Piano Transcriber (Transkun)"


def detect_hardware():
    info = {
        "cpu_name": platform.processor() or "Không xác định",
        "cpu_cores": os.cpu_count() or 1,
        "ram_gb": None,
        "gpu_available": False,
        "gpu_name": None,
        "gpu_vram_gb": None,
        "recommended_device": "cpu",
    }

    try:
        import psutil
        info["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        info["ram_gb"] = None

    try:
        import torch
        if torch.cuda.is_available():
            info["gpu_available"] = True
            info["gpu_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            info["gpu_vram_gb"] = round(props.total_memory / (1024 ** 3), 1)
            info["recommended_device"] = "cuda"
    except Exception:
        pass

    return info


def run_transkun_inprocess(input_path, output_path, device):
    """
    Goi truc tiep ham main() cua transkun trong cung tien trinh (khong dung
    subprocess/sys.executable), de tranh loi khi app da duoc dong goi thanh .exe
    (luc do sys.executable tro vao chinh file .exe nay chu khong phai python.exe).
    """
    from transkun.transcribe import main as transkun_main

    old_argv = sys.argv
    sys.argv = ["transkun", input_path, output_path, "--device", device]

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            transkun_main()
    except SystemExit as e:
        # argparse hoac sys.exit() co the duoc goi ben trong; code 0 la binh thuong
        if e.code not in (0, None):
            raise RuntimeError(
                f"transkun thoat voi ma loi {e.code}\n{stderr_buf.getvalue()}"
            )
    finally:
        sys.argv = old_argv

    if not os.path.isfile(output_path):
        raise RuntimeError(
            "transkun chay xong nhung khong thay file MIDI dau ra.\n"
            + stderr_buf.getvalue()[-1500:]
        )


class TranskunApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("580x430")
        self.resizable(False, False)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="San sang.")
        self.hw_info = detect_hardware()
        self.device = tk.StringVar(value=self.hw_info["recommended_device"])

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(pady=(14, 4))
        tk.Label(self, text="Chuyen file audio piano thanh MIDI bang model Transkun",
                 fg="#555").pack()

        hw_frame = tk.LabelFrame(self, text="Cau hinh may (tu dong nhan dien)", padx=10, pady=8)
        hw_frame.pack(fill="x", padx=10, pady=(12, 6))

        cpu_txt = f"CPU: {self.hw_info['cpu_name'][:40]}  ({self.hw_info['cpu_cores']} luong)"
        ram_txt = f"RAM: {self.hw_info['ram_gb']} GB" if self.hw_info["ram_gb"] else "RAM: khong do duoc"
        tk.Label(hw_frame, text=cpu_txt, anchor="w", justify="left").pack(fill="x")
        tk.Label(hw_frame, text=ram_txt, anchor="w", justify="left").pack(fill="x")

        if self.hw_info["gpu_available"]:
            gpu_txt = f"GPU: {self.hw_info['gpu_name']}  (VRAM: {self.hw_info['gpu_vram_gb']} GB)"
            gpu_color = "#0a8a0a"
            reco_txt = "-> Phat hien GPU NVIDIA, de xuat chay bang CUDA de nhanh hon."
        else:
            gpu_txt = "GPU: Khong phat hien GPU NVIDIA ho tro CUDA"
            gpu_color = "#b00"
            reco_txt = "-> Se chay bang CPU (cham hon nhung van hoat dong binh thuong)."

        tk.Label(hw_frame, text=gpu_txt, fg=gpu_color, anchor="w", justify="left").pack(fill="x", pady=(4, 0))
        tk.Label(hw_frame, text=reco_txt, fg="#555", anchor="w", justify="left",
                 font=("Segoe UI", 9, "italic")).pack(fill="x", pady=(2, 0))

        frm = tk.Frame(self)
        frm.pack(fill="x", **pad)

        tk.Label(frm, text="File audio dau vao:").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.input_path, width=48).grid(row=1, column=0, columnspan=2, sticky="we")
        tk.Button(frm, text="Chon file...", command=self.pick_input).grid(row=1, column=2, padx=6)

        tk.Label(frm, text="File MIDI dau ra:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frm, textvariable=self.output_path, width=48).grid(row=3, column=0, columnspan=2, sticky="we")
        tk.Button(frm, text="Chon noi luu...", command=self.pick_output).grid(row=3, column=2, padx=6)

        dev_frame = tk.Frame(self)
        dev_frame.pack(fill="x", **pad)
        tk.Label(dev_frame, text="Thiet bi xu ly:").pack(side="left")
        dev_values = ["cuda", "cpu"] if self.hw_info["gpu_available"] else ["cpu"]
        ttk.Combobox(dev_frame, textvariable=self.device, values=dev_values,
                     width=8, state="readonly").pack(side="left", padx=8)
        tk.Label(dev_frame, text="(tu dong chon theo may, co the doi tay)",
                 fg="#777", font=("Segoe UI", 8, "italic")).pack(side="left")

        self.run_btn = tk.Button(self, text="Bat dau Transcribe", bg="#2d7", fg="white",
                                  font=("Segoe UI", 11, "bold"), height=2, command=self.run_transcribe)
        self.run_btn.pack(fill="x", padx=10, pady=(16, 6))

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=4)

        tk.Label(self, textvariable=self.status, fg="#333").pack(pady=6)

    def pick_input(self):
        path = filedialog.askopenfilename(
            title="Chon file audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg"), ("Tat ca", "*.*")]
        )
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                base, _ = os.path.splitext(path)
                self.output_path.set(base + ".mid")

    def pick_output(self):
        path = filedialog.asksaveasfilename(
            title="Luu file MIDI",
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid")]
        )
        if path:
            self.output_path.set(path)

    def run_transcribe(self):
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()

        if not inp or not os.path.isfile(inp):
            messagebox.showerror("Loi", "Vui long chon file audio dau vao hop le.")
            return
        if not out:
            messagebox.showerror("Loi", "Vui long chon noi luu file MIDI.")
            return

        out_dir = os.path.dirname(out)
        if out_dir and not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Loi", f"Khong tao duoc thu muc dau ra:\n{e}")
                return

        self.run_btn.config(state="disabled")
        self.status.set("Dang xu ly, vui long doi (lan dau co the cham)...")
        self.progress.start(12)

        thread = threading.Thread(target=self._worker, args=(inp, out, self.device.get()))
        thread.daemon = True
        thread.start()

    def _worker(self, inp, out, device):
        try:
            run_transkun_inprocess(inp, out, device)
            self.after(0, self._on_success, out)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self, out):
        self.progress.stop()
        self.status.set(f"Hoan tat! Da luu: {out}")
        self.run_btn.config(state="normal")
        messagebox.showinfo("Xong", f"Transcribe thanh cong!\nFile MIDI: {out}")

    def _on_error(self, err):
        self.progress.stop()
        self.status.set("Co loi xay ra.")
        self.run_btn.config(state="normal")
        messagebox.showerror("Loi khi transcribe", err)


if __name__ == "__main__":
    app = TranskunApp()
    app.mainloop()
