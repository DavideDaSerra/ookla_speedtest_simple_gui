import os
import csv

from config import (
    HISTORY_FILE,
    MAX_HISTORY
)

from utils import get_base_dir


class HistoryManager:

    def __init__(self):

        self.server_history = []

        self.load()

    def load(self):

        self.server_history = []

        history_path = os.path.join(
            get_base_dir(),
            HISTORY_FILE
        )

        if not os.path.exists(history_path):
            return

        try:

            with open(
                history_path,
                "r",
                encoding="utf-8"
            ) as f:

                reader = csv.reader(
                    f,
                    delimiter="\t"
                )

                for row in reader:

                    if len(row) >= 2:

                        self.server_history.append(
                            (row[0], row[1])
                        )

        except Exception as e:

            print(e)

    def save(self):

        history_path = os.path.join(
            get_base_dir(),
            HISTORY_FILE
        )

        try:

            with open(
                history_path,
                "w",
                encoding="utf-8",
                newline=""
            ) as f:

                writer = csv.writer(
                    f,
                    delimiter="\t"
                )

                for server_id, server_name in self.server_history:

                    writer.writerow([
                        server_id,
                        server_name
                    ])

        except Exception as e:

            print(e)

    def add(
        self,
        server_id,
        server_name
    ):

        if not server_id:
            return

        server_id = str(server_id).strip()
        server_name = str(server_name).strip()

        new_history = []

        for sid, sname in self.server_history:

            sid = str(sid).strip()

            if sid != server_id:

                new_history.append(
                    (sid, sname)
                )

        self.server_history = new_history

        self.server_history.insert(
            0,
            (
                server_id,
                server_name
            )
        )

        self.server_history = (
            self.server_history[
                :MAX_HISTORY
            ]
        )

        self.save()
        