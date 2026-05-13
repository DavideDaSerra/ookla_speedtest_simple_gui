import tkinter as tk

from tkinter import (
    ttk,
    messagebox,
    Menu
)

import threading
import re
import sys

from config import (
    VERSIONE,
    AUTORE
)

from utils import get_app_version
from utils import get_app_author

from history_manager import (
    HistoryManager
)

from speedtest_runner import (
    run_speedtest
)


class SpeedtestGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            f"Speedtest GUI v{VERSIONE}"
        )

        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.debug_mode = (
            "--simple" not in sys.argv
        )

        self.history = (
            HistoryManager()
        )

        self.create_menu()
        self.create_widgets()

    def create_menu(self):

        menubar = Menu(self.root)

        self.recent_menu = Menu(
            menubar,
            tearoff=0
        )

        menubar.add_cascade(
            label="Server recenti",
            menu=self.recent_menu
        )

        info_menu = Menu(
            menubar,
            tearoff=0
        )

        info_menu.add_command(
            label="Informazioni",
            command=self.show_info
        )

        menubar.add_cascade(
            label="Info",
            menu=info_menu
        )

        self.root.config(menu=menubar)

        self.refresh_recent_menu()

    def create_widgets(self):

        frame_top = ttk.Frame(
            self.root,
            padding=10
        )

        frame_top.pack(fill="x")

        ttk.Label(
            frame_top,
            text="Server ID:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.server_id = tk.StringVar(
            value="auto"
        )

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

        frame_results.pack(
            fill="both",
            expand=True
        )

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

        if self.debug_mode:

            separator2 = ttk.Separator(
                self.root,
                orient="horizontal"
            )

            separator2.pack(
                fill="x",
                pady=5
            )

            ttk.Label(
                self.root,
                text="Output completo:",
                font=("Segoe UI", 10, "bold")
            ).pack(
                anchor="w",
                padx=10
            )

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

    def refresh_recent_menu(self):

        self.recent_menu.delete(0, "end")

        if not self.history.server_history:

            self.recent_menu.add_command(
                label="Nessun server recente"
            )

            return

        for server_id, server_name in self.history.server_history:

            label = (
                f"{server_id} - {server_name}"
            )

            self.recent_menu.add_command(
                label=label,
                command=lambda s=server_id:
                    self.server_id.set(s)
            )

    def start_test(self):

        self.start_button.config(
            state="disabled"
        )

        for field in self.fields.values():
            field.set("-")

        if self.debug_mode:

            self.output_text.delete(
                "1.0",
                tk.END
            )

        thread = threading.Thread(
            target=self.run_test_thread
        )

        thread.daemon = True
        thread.start()

    def run_test_thread(self):

        try:

            output = run_speedtest(
                self.server_id.get().strip(),
                self.debug_output
            )

            self.parse_output(output)

        except Exception as e:

            self.root.after(
                0,
                lambda err=str(e): messagebox.showerror(
                    "Errore",
                    str(err)
                )
            )

        finally:

            self.root.after(
                0,
                lambda:
                self.start_button.config(
                    state="normal"
                )
            )

    def debug_output(self, line):

        if self.debug_mode:

            self.root.after(
                0,
                self.append_output,
                line
            )

    def append_output(self, text):

        self.output_text.insert(
            tk.END,
            text
        )

        self.output_text.see(tk.END)

    def show_info(self):

        info_text = (
            f"Speedtest GUI\n\n"
            f"Versione: {get_app_version()}\n"
            f"Autore: {get_app_author()}\n"
            f"Crediti: speedtest.net"
        )

        messagebox.showinfo(
            "Informazioni",
            info_text
        )

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

        values = {}

        for key, pattern in patterns.items():

            match = re.search(
                pattern,
                text
            )

            if match:

                value = (
                    match.group(1)
                    .strip()
                )

                values[key] = value

                self.root.after(
                    0,
                    lambda k=key, v=value:
                    self.fields[k].set(v)
                )

        current_server_id = (
            self.server_id.get()
            .strip()
        )

        server_name = values.get(
            "Server",
            "Unknown"
        )

        detected_server_id = None

        id_match = re.search(
            r"\(id:\s*(\d+)\)",
            server_name,
            re.IGNORECASE
        )

        if id_match:

            detected_server_id = (
                id_match.group(1)
                .strip()
            )

        if (
            current_server_id and
            current_server_id.lower() != "auto"
        ):

            detected_server_id = (
                current_server_id
            )

        if detected_server_id:

            self.history.add(
                detected_server_id,
                server_name
            )

            self.refresh_recent_menu()


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
# Su linux: pyinstaller --onefile --windowed --add-data "bin:bin" gui.py
