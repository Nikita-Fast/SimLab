import json

from matplotlib import pyplot as plt

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
        self.start_process_signal.connect(self.start_many_processes)
        self.finished = 0

    def execute(self):
        self.start_process_signal.emit()

    def start_process(self):
        self.clear_results_folder()
        self.process = QProcess()
        self.process.finished.connect(self.process_finished)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.start("python3", ["./code_gen/generated.py"])

    def start_many_processes(self):
        self.clear_results_folder()
        for _ in range(self.threads_number):
            p = QProcess()
            p.finished.connect(self.process_finished)
            p.readyReadStandardOutput.connect(self.handle_stdout)
            p.start("python3", ["./code_gen/generated.py"])
            self.processes.append(p)

    def clear_results_folder(self):
        for root, dirs, files in os.walk(f"./modelling_output"):
            for f in files:
                try:
                    os.remove(f"{root}/{f}")
                except Exception as e:
                    pass

    def extract_and_plot_results(self):
        results = []
        for root, dirs, files in os.walk(f"./modelling_output"):
            for f in files:
                try:
                    with open(f"{root}/{f}", 'r') as json_file:
                        results.append(json.load(json_file))
                except Exception as e:
                    pass
        print("results:", results)
        ebn0_db_list = results[0]["BER Plotter"]["ebn0_db_list"]
        results = [dct["BER Plotter"]["ber_list"] for dct in results]

        plt.figure()
        plt.title("BER for each process")
        plt.yscale("log")
        plt.grid(visible='true')
        plt.xlabel("Eb/N0, dB")
        plt.ylabel("BER")
        for index, ber_list in enumerate(results):
            plt.plot(ebn0_db_list, ber_list, '--o', label=f"{index}")
        plt.legend()
        plt.show()

        for bers_for_fixed_ebn0 in zip(*results):
            assert len(bers_for_fixed_ebn0) == self.threads_number

        ber_list = [sum(bers_for_fixed_ebn0) / self.threads_number for bers_for_fixed_ebn0 in zip(*results)]
        print(ber_list, ebn0_db_list)
        plt.figure()
        plt.title("Resulted BER")
        plt.yscale("log")
        plt.grid(visible='true')
        plt.xlabel("Eb/N0, dB")
        plt.ylabel("BER")
        plt.plot(ebn0_db_list, ber_list, '--o', label='DEFAULT_NAME')

        plt.legend()
        plt.show()

    def process_finished(self):
        self.finished += 1
        print(f"Process finished")
        if self.finished == self.threads_number:
            self.extract_and_plot_results()
        self.process = None

    def handle_stdout(self):
        for p in self.processes:
            data = p.readAllStandardOutput()
            stdout = bytes(data).decode("utf8")
            print(stdout)
            self.write_message(stdout)

    def write_message(self, text: str):
        self.text_browser.append(f"\n{text}")
