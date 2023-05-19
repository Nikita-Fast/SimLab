import inspect
import os.path
import sys
from typing import Dict, Any, List

from gui.module_widget import ModuleWidget


def run_test_code_generation2(module_widget_to_vertex):
    g = BasicGenerator()
    g.process_model(module_widget_to_vertex)


class BasicGenerator:
    OUTPUT_FILE_NAME = 'code_gen/generated.py'

    def process_model(self, module_to_vertex: Dict[ModuleWidget, str]):

        code_lines = ['']
        modules: List[ModuleWidget] = [m for m in module_to_vertex.keys()]
        # import
        code_lines.append(f'from code_gen.utils import ModuleWrapper')
        code_lines.append(f'import networkx as nx')
        code_lines += self.gen_descriptors_import([m.module for m in modules])

        # load connection_graph
        code_lines.append('')
        connection_graph_name = 'connection_graph'
        path = 'code_gen/connection_graph.dot'
        code_lines.append(f'{connection_graph_name} = nx.drawing.nx_pydot.read_dot(\'{path}\')')

        # create dicts
        code_lines.append(f'id_to_module = dict()')
        code_lines.append(f'id_to_descriptor = dict()')

        # init modules
        code_lines.append('')
        for m in modules:
            code_lines += self.gen_module_init(m, module_to_vertex)

        # utils.ModuleWrapper
        code_lines += self.gen_module_wrapper_creation()
        code_lines += self.gen_source_modules_selection(connection_graph_name)

        # обход графа модели
        code_lines += self.gen_traversal_and_execution()

        # исследуем содержимое буфером модулей-стоков
        code_lines += self.gen_sink_modules_results_inspecting(connection_graph_name)

        code_lines += ['', f'print(\'EXECUTED\')']

        with open(self.OUTPUT_FILE_NAME, 'w') as f:
            f.write('\n'.join(code_lines))

        import code_gen.generated as gen
        # deimport module
        sys.modules.pop(gen.__name__)
        del gen

    def gen_sink_modules_results_inspecting(self, connection_graph_name: str):
        return [
            '',
            f'sink_module_wrappers = [m for m in module_wrapper_to_id if m.is_sink({connection_graph_name})]',
            'for m in sink_module_wrappers:',
            '\tprint(f\'module_id={m.get_id}, res={m.get_execution_results}\')'
        ]

    def gen_traversal_and_execution(self):
        return [
            '',
            'work_list = [*sources]',
            'while work_list:',
            '\tmodule_wrapper = work_list[0]',
            '\tmodule_wrapper.execute()',
            '\tmodule_wrapper.send_to_successors(connection_graph, module_wrapper_to_id)',
            '\twork_list += module_wrapper.successors(connection_graph, id_to_module_wrapper)',
            '\tdel(work_list[0])'
        ]

    def gen_module_wrapper_creation(self):
        return [
            '',
            'id_to_module_wrapper = dict()',
            'module_wrapper_to_id = dict()',
            'for id, module in id_to_module.items():',
            '\tm = ModuleWrapper(id_to_descriptor[id], module, id)',
            '\tid_to_module_wrapper[id] = m',
            '\tmodule_wrapper_to_id[m] = id'
        ]

    def gen_source_modules_selection(self, connection_graph_name: str):
        return [
            '',
            'sources = []',
            'for module_wrapper in id_to_module_wrapper.values():',
            f'\tif module_wrapper.is_source({connection_graph_name}):',
            '\t\tsources.append(module_wrapper)'
        ]

    def gen_descriptors_import(self, descriptors):
        lines = []
        for d in descriptors:
            module_dir_path = os.path.dirname(d.__file__)
            modules_root = 'modules'
            _, modules_root, after = module_dir_path.partition(modules_root)
            import_path = (modules_root + after).replace('/', '.')
            line = f'from {import_path} import {d.__name__}'
            lines.append(line)
        return lines

    def gen_module_init(
            self,
            module: ModuleWidget,
            module_to_vertex: Dict[ModuleWidget, str],
            params_from_gui={'init_params': {}}
    ) -> List[str]:
        descriptor = module.module
        lines = []
        module_type = getattr(descriptor, 'module_type', None)

        if module_type:
            module_id = module_to_vertex[module]
            obj_name = self.gen_module_name(module, module_id)

            obj_creation = ''
            if module_type == 'function':
                f_name = f'{descriptor.__name__}.{descriptor.entry_point.__name__}'
                obj_creation = f'{obj_name} = {f_name}'
            if module_type == 'class':
                module_class = getattr(descriptor, 'module_class')
                constructor_invocation = \
                    self.gen_module_constructor_invocation(descriptor, module_class, params_from_gui['init_params'])
                obj_creation = f'{obj_name} = {constructor_invocation}'

            lines.append(obj_creation)
            lines.append(f'id_to_module[\'{module_id}\'] = {obj_name}')
            lines.append(f'id_to_descriptor[\'{module_id}\'] = {descriptor.__name__}')

        return lines

    # истчоники параметров:
    # 1) GUI
    # 2) дескриптор
    def fetch_method_params(self, method_name: str, module_class: type, descriptor, params_from_gui: Dict[str, Any]):
        param_names = inspect.getfullargspec(module_class.__dict__[method_name]).args
        # у метода класса параметр self заполняется автоматически
        if 'self' in param_names:
            param_names.remove('self')

        param_to_value = {p_name: None for p_name in param_names}

        for p in params_from_gui:
            if p not in param_to_value.keys():
                raise Exception('через GUI передан параметр с именем отсутствующим среди имен параметров метода')
            else:
                param_to_value[p] = params_from_gui[p]

        for p_name in param_names:
            # значение параметра полученное от GUI приоритетнее чем значение параметра указанное в дескрипторе
            if param_to_value[p_name] is None:
                p_value = descriptor.__dict__.get(p_name, None)
                if p_value:
                    param_to_value[p_name] = p_value

        for p_name, p_value in param_to_value.items():
            if p_value is None:
                raise Exception(f'для параметра {p_name} значение не передано через GUI и не указано в дескрипторе')

        return param_to_value

    def gen_module_constructor_invocation(self, descriptor, module_class: type, params_from_gui: Dict[str, Any]):
        param_to_value = self.fetch_method_params('__init__', module_class, descriptor, params_from_gui)
        s_params = self.method_params_to_str(param_to_value)
        return f'{descriptor.__name__}.{module_class.__name__}({s_params})'

    def gen_module_name(self, module: ModuleWidget, module_id: str):
        descriptor = module.module
        name = descriptor.name.replace(' ', '')
        return f'module_{module_id}_{name}'

    def method_params_to_str(self, params: Dict[str, Any]) -> str:
        s = []
        for name, value in params.items():
            s.append(f'{name}={value}')
        return ', '.join(s)