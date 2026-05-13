import subprocess
import platform


from utils import (
    get_speedtest_executable
)


def run_speedtest(
    server_id=None,
    output_callback=None
):

    exe_path = (
        get_speedtest_executable()
    )

    cmd = [
        exe_path,
        "--accept-license",
        "--accept-gdpr"
    ]

    if (
        server_id and
        server_id.lower() != "auto"
    ):

        cmd.extend([
            "-s",
            server_id
        ])

    if platform.system().lower() == "windows":

        startupinfo = subprocess.STARTUPINFO()

        startupinfo.dwFlags |= (
            subprocess.STARTF_USESHOWWINDOW
        )

        creationflags = (
            subprocess.CREATE_NO_WINDOW
        )

    else:

        startupinfo = None
        creationflags = 0

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

    try:

        process.stdin.write("yes\n")
        process.stdin.flush()

    except:
        pass

    while True:

        line = (
            process.stdout.readline()
        )

        if not line:
            break

        full_output += line

        if output_callback:

            output_callback(line)

    process.wait()

    return full_output
