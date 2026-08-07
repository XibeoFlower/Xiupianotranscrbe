# Hướng dẫn chi tiết: Xây dựng App PC Transcribe Piano dùng Transkun

Tài liệu này hướng dẫn từ A-Z: cài môi trường, cài Transkun, chạy thử dòng lệnh, và **xây dựng một app PC có giao diện (GUI)** để chuyển audio piano thành file MIDI, kèm cách xử lý các lỗi hay gặp nhất.

Repo gốc: `https://github.com/Yujia-Yan/Transkun`

---

## 1. Yêu cầu hệ thống

- **Windows 10/11**, macOS, hoặc Linux đều được (hướng dẫn dưới đây tập trung Windows vì phổ biến nhất, có ghi chú cho Mac/Linux).
- **Python 3.9 – 3.12** (khuyến nghị 3.10 hoặc 3.11 để tránh xung đột thư viện).
- **FFmpeg** (bắt buộc, để đọc mp3/wav/m4a...).
- Ổ cứng trống ít nhất ~3GB (PyTorch khá nặng).
- GPU NVIDIA (tuỳ chọn) nếu muốn chạy nhanh hơn với CUDA. Không có GPU vẫn chạy được bằng CPU, chỉ chậm hơn.

---

## 2. Cài đặt Python

1. Vào `https://www.python.org/downloads/`, tải bản Python 3.11 (bản mới nhất ổn định).
2. Khi cài đặt trên Windows, **nhớ tick vào ô "Add python.exe to PATH"** ở màn hình đầu tiên — đây là lỗi phổ biến nhất khiến lệnh `python`/`pip` không chạy được sau này.
3. Kiểm tra sau khi cài, mở **Command Prompt (cmd)** hoặc **PowerShell**, gõ:
   ```
   python --version
   pip --version
   ```
   Nếu hiện số phiên bản là thành công.

---

## 3. Cài đặt FFmpeg (bắt buộc)

### Windows
1. Vào `https://www.gyan.dev/ffmpeg/builds/` → tải bản **"release full"** (file zip).
2. Giải nén, ví dụ ra `C:\ffmpeg`.
3. Thêm `C:\ffmpeg\bin` vào biến môi trường PATH:
   - Gõ "Environment Variables" vào Start Menu → **Edit the system environment variables** → **Environment Variables**.
   - Ở mục "System variables", chọn `Path` → **Edit** → **New** → dán `C:\ffmpeg\bin` → OK tất cả.
4. Mở **cmd mới** (phải mở cửa sổ mới để PATH cập nhật), gõ:
   ```
   ffmpeg -version
   ```
   Nếu hiện thông tin phiên bản là đã xong.

### macOS
```
brew install ffmpeg
```

### Linux (Debian/Ubuntu)
```
sudo apt update && sudo apt install ffmpeg
```

---

## 4. Tạo môi trường ảo (khuyến nghị mạnh — tránh xung đột thư viện)

Mở cmd/terminal tại thư mục bạn muốn làm việc, ví dụ `D:\PianoApp`:

```
cd D:\PianoApp
python -m venv venv
```

Kích hoạt môi trường ảo:

- Windows (cmd):
  ```
  venv\Scripts\activate
  ```
- Windows (PowerShell) — nếu báo lỗi "cannot be loaded because running scripts is disabled":
  ```
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  venv\Scripts\Activate.ps1
  ```
- macOS/Linux:
  ```
  source venv/bin/activate
  ```

Sau khi kích hoạt, đầu dòng lệnh sẽ có chữ `(venv)`.

---

## 5. Cài đặt PyTorch (nên cài trước, đúng phiên bản)

Cài PyTorch **trước** khi cài Transkun để tránh việc pip tự chọn bản CPU/GPU không đúng ý bạn.

- **Không có GPU / chỉ dùng CPU:**
  ```
  pip install torch --index-url https://download.pytorch.org/whl/cpu
  ```
- **Có GPU NVIDIA + đã cài CUDA driver:**
  Vào `https://pytorch.org/get-started/locally/`, chọn hệ điều hành + bản CUDA phù hợp, copy đúng lệnh (ví dụ):
  ```
  pip install torch --index-url https://download.pytorch.org/whl/cu124
  ```

Kiểm tra:
```
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

---

## 6. Cài đặt Transkun

```
pip install transkun
```

Kiểm tra nhanh bằng dòng lệnh có sẵn của Transkun:
```
transkun --help
```

Thử transcribe 1 file mp3/wav bất kỳ (đổi đường dẫn cho đúng):
```
transkun "D:\PianoApp\test.mp3" "D:\PianoApp\test.mid"
```
Nếu có GPU:
```
transkun "D:\PianoApp\test.mp3" "D:\PianoApp\test.mid" --device cuda
```

Nếu file `.mid` sinh ra được, mở bằng bất kỳ trình xem MIDI/DAW nào (MuseScore, FL Studio...) để kiểm tra — vậy là phần lõi đã chạy đúng.

**Lưu ý:** checkpoint mặc định của bản pip **không mở rộng nốt theo pedal** (no pedal extension), phù hợp để nghe/đối chiếu với bản trình diễn thật. Nếu muốn checkpoint khác (có pedal extension...), xem mục "Model Cards" trong repo GitHub và dùng cờ `--weight` để trỏ tới file weight tải riêng.

---

## 7. Xây dựng App PC có giao diện (GUI)

Có 2 lựa chọn:

### Lựa chọn A — Dùng GUI có sẵn trên GitHub (nhanh nhất)
- `natsunoshion/TranskunGUI` — giao diện Gradio (chạy trong trình duyệt local).
- `AIGLE25/Transkun-GUI` — GUI desktop riêng, hỗ trợ batch nhiều file, nhưng bạn vẫn phải tự cài Transkun + FFmpeg như hướng dẫn ở trên vì repo này **chỉ là phần giao diện**, không đóng gói sẵn backend.

Cách dùng chung: `git clone` repo đó về, đọc README của chính repo GUI đó để chạy (thường là `python app.py` hoặc tương tự), vì mỗi repo GUI có script khởi động khác nhau.

### Lựa chọn B — Tự viết app Tkinter (khuyên dùng nếu muốn full quyền kiểm soát, không phụ thuộc code người khác)

Tạo file `app.py` trong thư mục `D:\PianoApp` với nội dung sau:

```python
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
```

Cài thêm `psutil` (tuỳ chọn, để app hiển thị RAM máy — nếu không cài, app vẫn chạy bình thường, chỉ là không hiện dòng RAM):
```
pip install psutil
```

Chạy thử app:
```
python app.py
```

App này: **tự động dò cấu hình máy** (CPU, RAM, GPU) ngay khi mở lên và hiển thị trong khung "Cấu hình máy" ở trên cùng → nếu máy có GPU NVIDIA hỗ trợ CUDA, app tự đặt sẵn thiết bị xử lý là `cuda` để chạy nhanh hơn; nếu không có GPU, app tự đặt `cpu` và chỉ cho chọn `cpu` (ẩn lựa chọn cuda vì máy không hỗ trợ, tránh chọn nhầm gây lỗi). Người dùng vẫn có thể đổi tay giữa cpu/cuda nếu máy có cả hai. Sau đó: chọn file audio → chọn nơi lưu MIDI → bấm "Bắt đầu Transcribe" → chạy Transkun ở luồng nền (không đơ giao diện) → báo hoàn tất.

**Cách hoạt động của phần tự nhận diện:** app dùng `torch.cuda.is_available()` để kiểm tra xem máy có GPU NVIDIA + driver CUDA hợp lệ hay không, lấy tên GPU và dung lượng VRAM bằng `torch.cuda.get_device_properties()`. Đây chính là điều kiện Transkun cần để chạy được với `--device cuda`, nên nếu app báo "phát hiện GPU" thì chắc chắn dùng được cuda; nếu app báo không phát hiện, dùng cuda cũng sẽ báo lỗi nên app tự ẩn lựa chọn đó đi cho an toàn.

### Đóng gói thành file `.exe` chạy độc lập (Windows)

```
pip install pyinstaller
pyinstaller --onefile --windowed --name "PianoTranscriber" app.py
```

File `.exe` sẽ nằm trong thư mục `dist\`. Lưu ý:
- Máy chạy file `.exe` này **vẫn cần cài FFmpeg và thêm vào PATH** như bước 3, vì PyInstaller không tự đóng gói FFmpeg.
- File `.exe` khá nặng (do PyTorch), có thể 500MB–1GB+, đây là bình thường.
- Lần chạy đầu tiên có thể chậm vì Transkun cần load checkpoint.

---

## 8. Các lỗi thường gặp và cách khắc phục

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Chưa thêm Python vào PATH | Cài lại Python, tick "Add to PATH", hoặc tự thêm thủ công vào Environment Variables |
| `ModuleNotFoundError: No module named 'transkun'` | Chưa kích hoạt venv, hoặc cài nhầm môi trường | Kích hoạt lại `venv\Scripts\activate` rồi `pip install transkun` lại |
| `RuntimeError: No audio backend is available` hoặc lỗi đọc mp3 | Thiếu FFmpeg / FFmpeg chưa vào PATH | Cài FFmpeg đúng bước 3, mở cmd **mới** để PATH cập nhật |
| `CUDA out of memory` | GPU không đủ VRAM | Đổi `--device cpu`, hoặc giảm `--segmentSize`/`--segmentHopSize` khi chạy `transkun.transcribe` |
| `torch.cuda.is_available()` trả về `False` dù có GPU | Cài nhầm bản PyTorch CPU-only, hoặc thiếu driver NVIDIA/CUDA | Gỡ torch (`pip uninstall torch`), cài lại đúng lệnh CUDA từ pytorch.org, đảm bảo driver NVIDIA mới nhất |
| App Tkinter bị đơ ("Not Responding") khi transcribe | Chạy transcribe trực tiếp trên luồng giao diện chính | Đã xử lý trong code mẫu ở trên bằng `threading.Thread` — đừng gọi transkun trực tiếp trong hàm xử lý nút bấm |
| `pip install torch` chạy rất lâu hoặc lỗi mạng | Gói torch rất nặng (~2GB) | Kiên nhẫn đợi, hoặc dùng mạng ổn định hơn; có thể thử `pip install torch --index-url ... --timeout 1000` |
| PowerShell báo "cannot be loaded because running scripts is disabled" khi activate venv | Chính sách thực thi script của Windows | Chạy `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` trong PowerShell (với quyền user, không cần admin) |
| File `.exe` đóng gói không mở được hoặc báo thiếu file | PyInstaller không gom hết dữ liệu ẩn của torch/transkun | Thêm cờ `--collect-all torch --collect-all transkun` khi build: `pyinstaller --onefile --windowed --collect-all torch --collect-all transkun app.py` |
| Kết quả MIDI bị lệch nốt/thiếu pedal | Đây là checkpoint mặc định (no pedal extension) | Dùng checkpoint khác từ mục Model Cards trên GitHub kèm cờ `--weight` và `--conf` nếu cần khớp với quy ước có pedal extension |
| App báo "Không phát hiện GPU" dù máy có card NVIDIA | Cài nhầm bản PyTorch CPU-only, hoặc driver NVIDIA/CUDA chưa cài/lỗi thời | Gỡ `pip uninstall torch` rồi cài lại đúng bản CUDA theo bước 5; cập nhật driver NVIDIA mới nhất từ trang chủ NVIDIA |
| Dòng RAM trong app hiện "không dò được" | Chưa cài `psutil` | Chạy `pip install psutil` rồi mở lại app |
| Chọn `cuda` nhưng vẫn chạy chậm như CPU | Model chỉ chuyển một phần lên GPU, hoặc GPU đang bận job khác | Đóng các phần mềm dùng GPU khác, kiểm tra VRAM còn trống bằng lệnh `nvidia-smi` trong cmd |

---

## 9. Tóm tắt quy trình đầy đủ (copy chạy nhanh trên Windows)

```
cd D:\PianoApp
python -m venv venv
venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transkun
python app.py
```

(Nhớ đã cài FFmpeg và thêm vào PATH trước khi chạy các lệnh trên.)

---

Nếu bạn cho biết cụ thể lỗi gặp phải (copy nguyên đoạn lỗi trong cmd) hoặc bạn dùng CPU hay GPU nào, mình có thể chỉnh code/lệnh cho khớp chính xác với máy bạn.
