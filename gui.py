import subprocess
import threading
import re
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import platform


def get_speedtest_executable():

    

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    system_name = platform.system().lower()
    
    if system_name == "windows":
    
        exe_path = os.path.join(
            base_dir,
            "bin",
            "windows",
            "speedtest.exe"
        )
    
    elif system_name == "linux":
    
        exe_path = os.path.join(
            base_dir,
            "bin",
            "linux",
            "speedtest"
        )
    
    elif system_name == "darwin":
    
        exe_path = os.path.join(
            base_dir,
            "bin",
            "mac",
            "speedtest"
        )
    
    else:
        raise Exception(
            f"Sistema operativo non supportato: {system_name}"
        )
    
    if not os.path.exists(exe_path):
    
        raise Exception(
            f"Eseguibile non trovato:\n{exe_path}"
        )
    
    # Linux/Mac: assicura permessi esecuzione
    if system_name in ["linux", "darwin"]:
    
        try:
            os.chmod(exe_path, 0o755)
        except:
            pass
    
    return exe_path


class SpeedtestGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Speedtest GUI")
        self.root.geometry("750x350")
        self.root.resizable(False, False)

        # Modalità debug se presente -debug
        self.long_mode = "-long:true" not in sys.argv

        self.create_widgets()


    def create_widgets(self):

        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(fill="x")

        ttk.Label(
            frame_top,
            text="Server ID:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.server_id = tk.StringVar(value="auto")

        ttk.Entry(
            frame_top,
            textvariable=self.server_id,
            width=20
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        self.start_button = ttk.Button(
            frame_top,
            text="Test",
            command=self.start_test
        )

        self.start_button.grid(
            row=0,
            column=2,
            padx=10
        )

        separator = ttk.Separator(
            self.root,
            orient="horizontal"
        )

        separator.pack(fill="x", pady=5)

        frame_results = ttk.Frame(
            self.root,
            padding=10
        )

        frame_results.pack(fill="both", expand=True)

        self.fields = {}

        labels = [
            "Server",
            "ISP",
            "Idle Latency",
            "Download",
            "Upload",
            "Packet Loss",
            "Result URL"
        ]

        for idx, label in enumerate(labels):

            ttk.Label(
                frame_results,
                text=label + ":",
                font=("Segoe UI", 10, "bold")
            ).grid(
                row=idx,
                column=0,
                sticky="nw",
                pady=5
            )

            value = tk.StringVar(value="-")

            ttk.Label(
                frame_results,
                textvariable=value,
                font=("Consolas", 10),
                wraplength=550,
                justify="left"
            ).grid(
                row=idx,
                column=1,
                sticky="w",
                pady=5
            )

            self.fields[label] = value

        # Area output visibile SOLO in long
        if self.long_mode:

            separator2 = ttk.Separator(
                self.root,
                orient="horizontal"
            )

            separator2.pack(fill="x", pady=5)

            ttk.Label(
                self.root,
                text="Output completo:",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", padx=10)

            self.output_text = tk.Text(
                self.root,
                height=10
            )

            self.output_text.pack(
                fill="both",
                expand=True,
                padx=10,
                pady=5
            )

            self.root.geometry("750x550")

    def start_test(self):

        self.start_button.config(state="disabled")

        for field in self.fields.values():
            field.set("-")

        if self.long_mode:
            self.output_text.delete("1.0", tk.END)

        thread = threading.Thread(
            target=self.run_speedtest
        )

        thread.daemon = True
        thread.start()

    def run_speedtest(self):

        try:

            try:

                exe_path = get_speedtest_executable()

            except Exception as e:

                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Errore",
                        str(e)
                    )
                    )

                return

            cmd = [exe_path]

            server = self.server_id.get().strip()

            if server and server.lower() != "auto":
                cmd.extend(["-s", server, "--accept-gdpr"])

            # Nasconde completamente la console
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            creationflags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            full_output = ""

            # Risponde automaticamente yes
            try:
                process.stdin.write("yes\n")
                process.stdin.flush()
            except:
                pass

            while True:

                line = process.stdout.readline()

                if not line:
                    break

                full_output += line

                # Mostra output solo in long
                if self.long_mode:

                    self.root.after(
                        0,
                        self.append_output,
                        line
                    )

            process.wait()

            self.parse_output(full_output)

        except Exception as e:

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Errore",
                    str(e)
                )
            )

        finally:

            self.root.after(
                0,
                lambda: self.start_button.config(state="normal")
            )

    def append_output(self, text):

        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def parse_output(self, text):

        patterns = {
            "Server": r"Server:\s*(.*)",
            "ISP": r"ISP:\s*(.*)",
            "Idle Latency": r"Idle Latency:\s*(.*)",
            "Download": r"Download:\s*(.*)",
            "Upload": r"Upload:\s*(.*)",
            "Packet Loss": r"Packet Loss:\s*(.*)",
            "Result URL": r"Result URL:\s*(.*)"
        }

        for key, pattern in patterns.items():

            match = re.search(pattern, text)

            if match:

                value = match.group(1).strip()

                self.root.after(
                    0,
                    lambda k=key, v=value: self.fields[k].set(v)
                )


if __name__ == "__main__":

    root = tk.Tk()

    style = ttk.Style()
    style.theme_use("clam")

    app = SpeedtestGUI(root)

    root.mainloop()


####### NOTE: per eseguire come programma
    # rinominare in .pyw (non apre la consolle

    # con pyinstaller:
    # c:>pip install -U pyinstaller
    # pyinstaller --onefile --noconsole --add-data "bin;bin" gui.py
    # oppure
    # pyinstaller --onefile --windowed --add-data "bin;bin" gui.py

    #se non trova pyinstaller nel path:
    # python -m PyInstaller --onefile --windowed --add-data "bin;bin" gui.py
