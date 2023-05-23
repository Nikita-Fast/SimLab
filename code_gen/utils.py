import inspect
import json
from typing import Dict, List
import networkx as nx


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


class ModuleWrapper:
    def __init__(self, descriptor, module_obj, id: int):
        # module_obj это объект модуль создаваемый в генерируемом коде т.е. например module0_AWGNChannel
        self.descriptor = descriptor
        self._f = descriptor.entry_point
        self._module_obj = module_obj
        self._buffer = [None] * len(getattr(self.descriptor, 'input_ports', []))
        self._exec_res = [None] * len(getattr(self.descriptor, 'output_ports', []))
        # имя вершины в connection_graph, которой соответствует этот модуль
        self._id = id

    def put(self, input_port_id: int, data):
        # положить данные на указанный вход
        self._buffer[input_port_id] = data

    def get(self, output_port_id: int):
        # получить значение с указанного выхода
        return self._exec_res[output_port_id]

    @property
    def get_execution_results(self):
        return self._exec_res

    @property
    def get_id(self):
        return self._id

    def execute(self):
        for output_port_number in range(len(self._exec_res)):
            # Выбираем функцию-вычислитель. Если в дескрипторе явно не указана функцию-вычислитель,
            # то по умолчанию используется descriptor.entry_point
            f = self.descriptor.output_ports[output_port_number].get('f', self._f)

            # выбираем входные порты, с которых возьмем параметры для вызова функции-вычислителя
            # если номера портов не указаны в дескрипторе явно, то берем первые k портов,
            # где k - число параметров функции
            f_param_name_to_value = {p_name: None for p_name in inspect.getfullargspec(f).args}
            if 'self' in f_param_name_to_value:
                del (f_param_name_to_value['self'])
            assert ('self' not in f_param_name_to_value)

            first_k_inputs = [i for i, _ in enumerate(f_param_name_to_value)]
            inputs: List[int] = self.descriptor.output_ports[output_port_number].get('inputs', first_k_inputs)

            # берем значения параметров из буфера
            for i, p_name in enumerate(f_param_name_to_value):
                input_port_number = inputs[i]
                if input_port_number < len(self._buffer):
                    f_param_name_to_value[p_name] = self._buffer[input_port_number]

            # смотрим значения параметров прямо в дескрипторе
            for p_name, p_value in f_param_name_to_value.items():
                if p_value is None:
                    f_param_name_to_value[p_name] = self.descriptor.__dict__.get(p_name, None)

            # для параметров не получивших значение, смотрим указано ли значение по умолчанию
            default_args = get_default_args(f)
            for p_name in f_param_name_to_value:
                if f_param_name_to_value[p_name] is None:
                    p_value = default_args.get(p_name, None)
                    if p_value:
                        f_param_name_to_value[p_name] = p_value

            for p_name, p_value in f_param_name_to_value.items():
                if p_name not in default_args and p_value is None:
                    raise Exception(f'для параметра {p_name}, не имеющего значения по умолчанию, '
                                    f'значение не передано через GUI и не указано в дескрипторе')

            # извлекаем значения параметров
            params = [*f_param_name_to_value.values()]

            # методу класса нужно передать объект
            if self.descriptor.module_type == 'class':
                params.insert(0, self._module_obj)

            # выполняем вычисления
            self._exec_res[output_port_number] = f(*params)


class FlowGraph:
    # flowgraph это граф, вершины которого это реальные модули (а не виджеты)
    # цель flowgraph-а это управление потоком данных в моделе и контроль порядка работы модулей
    def __init__(self, modules: List[ModuleWrapper], *args, **kwargs):
        self.modules = modules
        self.connections = self.load_port_connections_info()

    def load_port_connections_info(self):
        with open('./code_gen/connections.json') as file:
            connections = json.load(file)
            # json превращает int-овые ключи в строковые, поэтому требуется распарсить int
            return {int(src_module_id): v for src_module_id, v in connections.items()}

    def is_source_module(self, module: ModuleWrapper):
        # У блока источника нет ВХОДНЫХ ПОРТОВ
        input_port_number = len(module.descriptor.__dict__.get('input_ports', []))
        return input_port_number == 0

    def is_sink_module(self, module: ModuleWrapper):
        # У блока являющегося стоком нет ИСХОДЯЩИХ СОЕДИНЕНИЙ, т.е. могут быть не подключенные выходные порты
        module_output_connections = self.connections[module.get_id]
        for output_port in module_output_connections:
            if output_port['is_connected']:
                return False
        return True

    def send_module_data_to_successors(self, src_module: ModuleWrapper):
        module_output_connections = self.connections[src_module.get_id]
        for output_port in module_output_connections:
            if output_port['is_connected']:
                dst_module_id = output_port['dst_module_id']
                dst_module = self.modules[dst_module_id]

                data = src_module.get(output_port_id=output_port['src_output_port_id'])
                dst_module.put(input_port_id=output_port['dst_input_port_id'], data=data)

    def get_module_successors(self, module: ModuleWrapper):
        successors = []
        module_output_connections = self.connections[module.get_id]
        for output_port in module_output_connections:
            if output_port['is_connected']:
                dst_module_id = output_port['dst_module_id']
                dst_module = self.modules[dst_module_id]
                successors.append(dst_module)
        return successors

    def run(self):
        source_modules = [module for module in self.modules if self.is_source_module(module)]

        work_list = [*source_modules]
        while work_list:
            module = work_list[0]
            # todo join модули, у которых есть незаполненные input_ports
            module.execute()
            self.send_module_data_to_successors(module)
            work_list += self.get_module_successors(module)
            del (work_list[0])

        sink_modules = [module for module in self.modules if self.is_sink_module(module)]
        for m in sink_modules:
            print(f'module_id={m.get_id}, res={m.get_execution_results}')










