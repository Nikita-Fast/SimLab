import inspect
import os.path
import sys
from typing import Dict, Any, List

from gui.module_widget import ModuleWidget


def run_test_code_generation2(module_widgets):
    g = BasicGenerator()
    g.process_model(module_widgets)


class BasicGenerator:
    OUTPUT_FILE_NAME = 'code_gen/generated.py'

    def process_model(self, module_widgets: List[ModuleWidget]):
        code_lines = ['']
        modules = module_widgets
        # import
        code_lines.append(f'from code_gen.utils import ModuleWrapper, FlowGraph')
        code_lines.append(f'import networkx as nx')
        code_lines += self.gen_descriptors_import([m.module for m in modules])

        # create dicts
        code_lines.append(f'id_to_module = dict()')
        code_lines.append(f'id_to_descriptor = dict()')

        # init modules
        code_lines.append('')
        for module_id, m in enumerate(modules):
            code_lines += self.gen_module_init(m, module_id)

        # utils.ModuleWrapper
        code_lines += self.gen_module_wrapper_creation()

        # создать и запустить flow_graph
        code_lines += self.gen_flow_graph_creation()

        code_lines += ['', f'print(\'EXECUTED\')']

        with open(self.OUTPUT_FILE_NAME, 'w') as f:
            f.write('\n'.join(code_lines))

        import code_gen.generated as gen
        # deimport module
        sys.modules.pop(gen.__name__)
        del gen

    def gen_module_wrapper_creation(self):
        return [
            '',
            'module_wrappers = []',
            'for id, module in id_to_module.items():',
            '\tm = ModuleWrapper(id_to_descriptor[id], module, id)',
            '\tmodule_wrappers.append(m)',
        ]

    def gen_flow_graph_creation(self):
        return [
            '',
            'flow_graph = FlowGraph(modules=module_wrappers)',
            'flow_graph.run()',
        ]

    def gen_descriptors_import(self, descriptors):
        lines = []
        for d in descriptors:
            module_dir_path = os.path.dirname(d.__file__)
            modules_root = 'modules'
            _, modules_root, after = module_dir_path.partition(modules_root)
            import_path = (modules_root + after).replace('/', '.')
            import_name = os.path.splitext(d.__file__)[0].split('/')[-1]
            line = f'from {import_path} import {import_name}'
            lines.append(line)
        return lines

    def gen_module_init(
            self,
            module: ModuleWidget,
            module_id: int
    ) -> List[str]:
        descriptor = module.module
        lines = []
        module_type = getattr(descriptor, 'module_type', None)

        if module_type:
            obj_name = self.gen_module_name(module, module_id)

            descriptor_name = os.path.splitext(descriptor.__file__)[0].split('/')[-1]
            obj_creation = ''

            # достаем параметры из gui и сохраняем их в дескрипторе
            if module_gui := module.module.__dict__.get('gui'):
                params_from_gui = module_gui.get_param_values()
                self.save_params_from_gui_to_descriptor(params_from_gui, descriptor)

            if module_type == 'function':
                f_name = f'{descriptor_name}.{descriptor.entry_point.__name__}'
                obj_creation = f'{obj_name} = {f_name}'
            if module_type == 'class':
                module_class = getattr(descriptor, 'module_class')
                constructor_invocation = self.gen_module_constructor_invocation(descriptor, module_class)
                obj_creation = f'{obj_name} = {constructor_invocation}'

            lines.append(obj_creation)
            lines.append(f'id_to_module[{module_id}] = {obj_name}')
            lines.append(f'id_to_descriptor[{module_id}] = {descriptor_name}')

        return lines

    def get_default_args(self, func):
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }

    def save_params_from_gui_to_descriptor(self, params_from_gui: Dict[str, Any], descriptor):
        for param_name, dct in params_from_gui.items():
            # Если значение параметры было выставлено на GUI, то пишем этот параметр в дескриптор
            if dct['param_is_set']:
                descriptor.__dict__[param_name] = dct['param_value']

    def fetch_method_params(self, method_name: str, module_class: type, descriptor):
        method = module_class.__dict__[method_name]
        param_names = inspect.getfullargspec(method).args

        # у метода класса параметр self заполняется автоматически
        if 'self' in param_names:
            param_names.remove('self')

        param_to_value = {p_name: None for p_name in param_names}

        for p_name in param_names:
            # Значение параметра полученное от GUI приоритетнее чем значение параметра указанное в дескрипторе
            # т.к. оно переписывает значение параметра, ранее указанное в дескрипторе
            p_value = descriptor.__dict__.get(p_name)
            if p_value:
                param_to_value[p_name] = p_value

        # для параметров не получивших значение, смотрим указано ли значение по умолчанию
        default_args = self.get_default_args(method)
        for p_name in param_names:
            if param_to_value[p_name] is None:
                p_value = default_args.get(p_name)
                if p_value:
                    param_to_value[p_name] = p_value

        for p_name, p_value in param_to_value.items():
            if p_name not in default_args and p_value is None:
                raise Exception(f'для параметра {p_name}, не имеющего значения по умолчанию, '
                                f'значение не передано через GUI и не указано в дескрипторе')

        return param_to_value

    def gen_module_constructor_invocation(self, descriptor, module_class: type):
        param_to_value = self.fetch_method_params('__init__', module_class, descriptor)
        print(param_to_value)
        s_params = self.method_params_to_str(param_to_value)
        descriptor_name = os.path.splitext(descriptor.__file__)[0].split('/')[-1]
        return f'{descriptor_name}.{module_class.__name__}({s_params})'

    def gen_module_name(self, module: ModuleWidget, module_id: int):
        descriptor = module.module
        name = descriptor.name.replace(' ', '')
        return f'module_{module_id}_{name}'

    def method_params_to_str(self, params: Dict[str, Any]) -> str:
        s = []
        for name, value in params.items():
            if isinstance(value, str):
                s.append(f'{name}=\'{value}\'')
            else:
                s.append(f'{name}={value}')
        return ', '.join(s)
