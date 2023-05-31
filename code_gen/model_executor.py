from qt import *
import os


class ModelExecutor(QObject):
    start_process_signal = Signal()

    def __init__(self, threads_number: int, text_browser: QTextBrowser):
        super().__init__()
        self.threads_number = threads_number
        self.text_browser = text_browser
        self.processes = []
        self.process = None
        self.start_process_signal.connect(self.start_process)

    def execute(self):
        print(f"proc {os.getpid()}: execute")
        self.start_process_signal.emit()

    def start_process(self):
        print(f"proc {os.getpid()}: start_process")
        self.process = QProcess()
        self.process.finished.connect(self.process_finished)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.start("python3", ["./code_gen/dummy.py"])

    def process_finished(self):
        self.process = None
        self.write_message(f"Process finished")

    def handle_stdout(self):
        # for p in self.processes:
        #     data = p.readAllStandardOutput()
        #     stdout = bytes(data).decode("utf8")
        #     self.write_message(stdout)
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
        self.write_message(stdout)

    def write_message(self, text: str):
        self.text_browser.append(text)

