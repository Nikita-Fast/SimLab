from matplotlib import pyplot as plt

name = "BER Plotter"
language = "Python"

ber_list = []
ebn0_db_list = []


def save(ber, ebn0_db):
    # print(f"inv with ber={ber} and ebn0={ebn0_db}")

    ber_list.append(ber)
    ebn0_db_list.append(ebn0_db)


module_type = 'function'
entry_point = save

input_ports = [
    {
        "label": "BER",
        "type": float
    },
    {
        "label": "Eb/N0 (db)",
        "type": int
    }
]

module_parameters = []

# флаг указывающий на то, что модуль является хранилищем данных
is_saving_data_between_iterations = True


def plot_ber():
    if len(ebn0_db_list) != len(ber_list):
        raise ValueError('Число значений по оси Х должно быть равно числу значений по оси У')
    plt.yscale("log")
    plt.grid(visible='true')
    plt.xlabel("Eb/N0, dB")
    plt.ylabel("BER")
    plt.plot(ebn0_db_list, ber_list, '--o', label='DEFAULT_NAME')
    ebn0_db_list.clear()
    ber_list.clear()
    plt.legend()
    plt.show()


# функция, указанная в "data_processor" вызывается модулем хранилищем после завершения всех итераций моделирования
# data_processor = lambda: print(f"Data storage content: {data_storage}")
data_processor = plot_ber
