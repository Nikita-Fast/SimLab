import inspect
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
    def __init__(self, descriptor, module_obj, id: str):
        # module_obj это объект модуль создаваемый в генерируемом коде т.е. например module0_AWGNChannel
        self.descriptor = descriptor
        self._f = descriptor.entry_point
        self._module_obj = module_obj
        self._buffer = [None] * len(getattr(self.descriptor, 'input_ports', []))
        self._exec_res = [None] * len(getattr(self.descriptor, 'output_ports', []))
        # имя вершины в connection_graph, которой соответствует этот модуль
        self._id = id

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

    def _send(self, src_port_num: int, dst_module: 'ModuleWrapper', dst_port_num: int):
        dst_module._buffer[dst_port_num] = self._exec_res[src_port_num]

    def send_to_successors(
            self,
            connection_graph: nx.MultiDiGraph,
            module_wrapper_to_vertex: Dict['ModuleWrapper', str]
    ):
        vertex_to_module_wrapper: Dict[str, 'ModuleWrapper'] = {v: m for m, v in module_wrapper_to_vertex.items()}
        src_vertex = self._id
        # в прочитанном графе вершины будет не int, а str(int)
        for dst_vertex in connection_graph.successors(src_vertex):
            dst_vertex: str
            for u, v, data in connection_graph.edges(data=True):
                if u == src_vertex and v == dst_vertex:
                    dst_module_wrapper = vertex_to_module_wrapper[dst_vertex]
                    input_port_num = int(data['input_num'])
                    output_port_num = int(data['output_num'])
                    self._send(input_port_num, dst_module_wrapper, output_port_num)

    def successors(
            self,
            connection_graph: nx.MultiDiGraph,
            vertex_to_module_wrapper: Dict[str, 'ModuleWrapper']
    ):
        return [vertex_to_module_wrapper[n] for n in connection_graph.successors(self._id)]

    # def _clear_buffer(self):
    #     self._buffer = [None] * len(self.descriptor.input_ports)

    @property
    def get_execution_results(self):
        return self._exec_res

    def is_source(self, connection_graph: nx.MultiDiGraph):
        self_vertex = self._id
        return (
                len(self._buffer) == 0 and len(self._exec_res) > 0 and
                len(connection_graph.in_edges(self_vertex)) == 0 and
                len(connection_graph.out_edges(self_vertex)) > 0
        )

    def is_sink(self, connection_graph: nx.MultiDiGraph):
        self_vertex = self._id
        return (
                len(self._buffer) > 0 and
                (len(self._exec_res) == 0 or len(connection_graph.out_edges(self_vertex)) == 0)
        )

    @property
    def get_id(self):
        return self._id
