import os
import sys
import platform
import config

def get_base_dir():

    if getattr(sys, 'frozen', False):

        return os.path.dirname(
            sys.executable
        )

    return os.path.dirname(
        os.path.abspath(__file__)
    )


def get_resource_dir():

    if getattr(sys, 'frozen', False):

        return sys._MEIPASS

    return os.path.dirname(
        os.path.abspath(__file__)
    )


def get_speedtest_executable():

    base_dir = get_resource_dir()

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

    if system_name in ["linux", "darwin"]:

        try:
            os.chmod(exe_path, 0o755)
        except:
            pass

    return exe_path


def get_app_version():

    # =====================================
    # Esecuzione come EXE PyInstaller
    # =====================================

    if getattr(sys, 'frozen', False):

        try:

            from win32api import (
                GetFileVersionInfo,
                LOWORD,
                HIWORD
            )

            exe_path = sys.executable

            info = GetFileVersionInfo(
                exe_path,
                "\\"
            )

            ms = info['FileVersionMS']
            ls = info['FileVersionLS']

            version = "%d.%d.%d.%d" % (
                HIWORD(ms),
                LOWORD(ms),
                HIWORD(ls),
                LOWORD(ls)
            )

            return version

        except Exception:

            pass

    # =====================================
    # Fallback sviluppo
    # =====================================

    try:

        from config import VERSIONE

        return VERSIONE

    except:

        return "0.0.0"


def get_app_author():
    return config.AUTORE

## todo: sistemare questa funzione per leggere il version_info
