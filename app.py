import os
import threading
import subprocess
import sys
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Piano Transcriber (Transkun)"


def detect_hardware():
    """
    Tự dò cấu hình máy: CPU, RAM, và GPU (CUDA) nếu có.
    Trả về dict thông tin + device đề xuất ('cuda' hoặc 'cpu').
    """
    info = {
        "cpu_name": platform.processor() or "Không xác định",
        "cpu_cores": os.cpu_count() or 1,
        "ram_gb": None,
        "gpu_available": False,
        "gpu_name": None,
        "gpu_vram_gb": None,
        "recommended_device": "cpu",
    }

    # RAM (không bắt buộc psutil, dò bằng cách khác nếu không có)
    try:
        import psutil
        info["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        info["ram_gb"] = None

    # GPU qua torch/CUDA
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


class TranskunApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("580x430")
        self.resizable(False, False)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Sẵn sàng.")
        self.hw_info = detect_hardware()
        self.device = tk.StringVar(value=self.hw_info["recommended_device"])

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(pady=(14, 4))
        tk.Label(self, text="Chuyển file audio piano thành MIDI bằng model Transkun",
                 fg="#555").pack()

        # --- Khung thông tin phần cứng tự động dò được ---
        hw_frame = tk.LabelFrame(self, text="Cấu hình máy (tự động nhận diện)", padx=10, pady=8)
        hw_frame.pack(fill="x", padx=10, pady=(12, 6))

        cpu_txt = f"CPU: {self.hw_info['cpu_name'][:40]}  ({self.hw_info['cpu_cores']} luồng)"
        ram_txt = f"RAM: {self.hw_info['ram_gb']} GB" if self.hw_info["ram_gb"] else "RAM: không dò được"
        tk.Label(hw_frame, text=cpu_txt, anchor="w", justify="left").pack(fill="x")
        tk.Label(hw_frame, text=ram_txt, anchor="w", justify="left").pack(fill="x")

        if self.hw_info["gpu_available"]:
            gpu_txt = f"GPU: {self.hw_info['gpu_name']}  (VRAM: {self.hw_info['gpu_vram_gb']} GB)"
            gpu_color = "#0a8a0a"
            reco_txt = "→ Phát hiện GPU NVIDIA, đề xuất chạy bằng CUDA để nhanh hơn."
        else:
            gpu_txt = "GPU: Không phát hiện GPU NVIDIA hỗ trợ CUDA"
            gpu_color = "#b00"
            reco_txt = "→ Sẽ chạy bằng CPU (chậm hơn nhưng vẫn hoạt động bình thường)."

        tk.Label(hw_frame, text=gpu_txt, fg=gpu_color, anchor="w", justify="left").pack(fill="x", pady=(4, 0))
        tk.Label(hw_frame, text=reco_txt, fg="#555", anchor="w", justify="left",
                 font=("Segoe UI", 9, "italic")).pack(fill="x", pady=(2, 0))

        frm = tk.Frame(self)
        frm.pack(fill="x", **pad)

        # Input file
        tk.Label(frm, text="File audio đầu vào:").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.input_path, width=48).grid(row=1, column=0, columnspan=2, sticky="we")
        tk.Button(frm, text="Chọn file...", command=self.pick_input).grid(row=1, column=2, padx=6)

        # Output file
        tk.Label(frm, text="File MIDI đầu ra:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frm, textvariable=self.output_path, width=48).grid(row=3, column=0, columnspan=2, sticky="we")
        tk.Button(frm, text="Chọn nơi lưu...", command=self.pick_output).grid(row=3, column=2, padx=6)

        # Device (đã tự chọn sẵn theo phần cứng, nhưng vẫn cho đổi tay)
        dev_frame = tk.Frame(self)
        dev_frame.pack(fill="x", **pad)
        tk.Label(dev_frame, text="Thiết bị xử lý:").pack(side="left")
        dev_values = ["cuda", "cpu"] if self.hw_info["gpu_available"] else ["cpu"]
        ttk.Combobox(dev_frame, textvariable=self.device, values=dev_values,
                     width=8, state="readonly").pack(side="left", padx=8)
        tk.Label(dev_frame, text="(tự động chọn theo máy, có thể đổi tay)",
                 fg="#777", font=("Segoe UI", 8, "italic")).pack(side="left")

        # Run button
        self.run_btn = tk.Button(self, text="Bắt đầu Transcribe", bg="#2d7", fg="white",
                                  font=("Segoe UI", 11, "bold"), height=2, command=self.run_transcribe)
        self.run_btn.pack(fill="x", padx=10, pady=(16, 6))

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=4)

        tk.Label(self, textvariable=self.status, fg="#333").pack(pady=6)

    def pick_input(self):
        path = filedialog.askopenfilename(
            title="Chọn file audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg"), ("Tất cả", "*.*")]
        )
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                base, _ = os.path.splitext(path)
                self.output_path.set(base + ".mid")

    def pick_output(self):
        path = filedialog.asksaveasfilename(
            title="Lưu file MIDI",
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid")]
        )
        if path:
            self.output_path.set(path)

    def run_transcribe(self):
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()

        if not inp or not os.path.isfile(inp):
            messagebox.showerror("Lỗi", "Vui lòng chọn file audio đầu vào hợp lệ.")
            return
        if not out:
            messagebox.showerror("Lỗi", "Vui lòng chọn nơi lưu file MIDI.")
            return

        self.run_btn.config(state="disabled")
        self.status.set("Đang xử lý, vui lòng đợi (lần đầu có thể chậm)...")
        self.progress.start(12)

        thread = threading.Thread(target=self._worker, args=(inp, out, self.device.get()))
        thread.daemon = True
        thread.start()

    def _worker(self, inp, out, device):
        try:
            cmd = [sys.executable, "-m", "transkun.transcribe", inp, out, "--device", device]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(result.stderr[-2000:] if result.stderr else "Lỗi không xác định.")

            self.after(0, self._on_success, out)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self, out):
        self.progress.stop()
        self.status.set(f"Hoàn tất! Đã lưu: {out}")
        self.run_btn.config(state="normal")
        messagebox.showinfo("Xong", f"Transcribe thành công!\nFile MIDI: {out}")

    def _on_error(self, err):
        self.progress.stop()
        self.status.set("Có lỗi xảy ra.")
        self.run_btn.config(state="normal")
        messagebox.showerror("Lỗi khi transcribe", err)


if __name__ == "__main__":
    app = TranskunApp()
    app.mainloop()
