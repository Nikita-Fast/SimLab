import inspect
import itertools
import json
import os.path
import sys
from typing import Dict, Any, List
from multiprocessing import Process, Queue, cpu_count

from matplotlib import pyplot as plt

from gui.module_widget import ModuleWidget


def run_test_code_generation2(module_widgets, threads_number: int):
    g = BasicGenerator()
    g.generate_modelling_code(module_widgets, threads_number)


def run_modelling_code():
    import code_gen.generated as gen
    gen.f()
    # deimport module
    sys.modules.pop(gen.__name__)
    del gen


def run_concurrently(threads_number: int, min_ebn0_db: int, max_ebn0_db: int):
    print(cpu_count())
    for root, dirs, files in os.walk(f"./modelling_output"):
        for f in files:
            try:
                os.remove(f"{root}/{f}")
            except Exception as e:
                pass

    if __name__ == 'code_gen.basic':
        processes = []
        for i in range(threads_number):
            p = Process(target=run_modelling_code, args=())
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
            p.close()

        results = []
        for root, dirs, files in os.walk(f"./modelling_output"):
            for f in files:
                try:
                    with open(f"{root}/{f}", 'r') as json_file:
                        results.append(json.load(json_file))
                except Exception as e:
                    pass
        # print(results)
        ebn0_db_list = results[0]["BER Plotter"]["ebn0_db_list"]
        results = [dct["BER Plotter"]["ber_list"] for dct in results]

        plt.figure()
        plt.yscale("log")
        plt.grid(visible='true')
        plt.xlabel("Eb/N0, dB")
        plt.ylabel("BER")
        for index, ber_list in enumerate(results):
            plt.plot(ebn0_db_list, ber_list, '--o', label=f"{index}")
        plt.legend()
        plt.show()

        for bers_for_fixed_ebn0 in zip(*results):
            assert len(bers_for_fixed_ebn0) == threads_number

        ber_list = [sum(bers_for_fixed_ebn0) / threads_number for bers_for_fixed_ebn0 in zip(*results)]
        print(ber_list, ebn0_db_list)
        plt.figure()
        plt.yscale("log")
        plt.grid(visible='true')
        plt.xlabel("Eb/N0, dB")
        plt.ylabel("BER")
        plt.plot(ebn0_db_list, ber_list, '--o', label='DEFAULT_NAME')

        plt.legend()
        plt.show()


class BasicGenerator:
    OUTPUT_FILE_NAME = 'code_gen/generated.py'

    def generate_modelling_code(self, module_widgets: List[ModuleWidget], threads_number: int):
        modules = module_widgets
        # import
        import_lines = [
            f"import sys",
            f"from code_gen.utils import ModuleWrapper, FlowGraph",
            f"from modelling_utils.custom_exceptions import *",
            f"import sys"
        ]
        import_lines += self.gen_descriptors_import([m.module for m in modules])

        # create dicts
        code_lines = [
            f'id_to_module = dict()',
            f'id_to_descriptor = dict()',
            ''
        ]

        # init modules
        for module_id, m in enumerate(modules):
            code_lines += self.gen_module_init(m, module_id)

        # utils.ModuleWrapper
        code_lines += self.gen_module_wrapper_creation(threads_number)

        # создать и запустить flow_graph
        code_lines += self.gen_flow_graph_creation_and_processing()

        # оборачиваем код моделирования вызовом функции
        code_lines = self.gen_function('f', code_lines)

        code_lines += ["", "f()"]

        with open(self.OUTPUT_FILE_NAME, 'w') as f:
            f.write('\n'.join(itertools.chain(import_lines, code_lines)))

    def gen_function(self, func_name: str, body: List[str]):
        return ["", "", f"def {func_name}():", *[f"\t{line}" for line in body]]

    def gen_module_wrapper_creation(self, threads_number: int):
        return [
            '',
            'module_wrappers = []',
            'for id, module in id_to_module.items():',
            f'\tm = ModuleWrapper(id_to_descriptor[id], module, id, {threads_number})',
            '\tmodule_wrappers.append(m)',
        ]

    def gen_flow_graph_creation_and_processing(self):
        #   flow_graph = FlowGraph(modules=module_wrappers)
        # 	while True:
        # 		try:
        # 			flow_graph.run()
        # 		except SourceModuleRunOutOfDataException as e:
        #           flow_graph.execute_storage_modules()
        # 			print('<><><>MODELLING DONE<><><>')
        # 			break
        return [
            "",
            "flow_graph = FlowGraph(modules=module_wrappers)",
            "while True:",
            "\ttry:",
            "\t\tflow_graph.run()",
            "\texcept SourceModuleRunOutOfDataException as e:",
            "\t\tflow_graph.execute_storage_modules()",
            "\t\tbreak",
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
        s_params = self.method_params_to_str(param_to_value)
        descriptor_name = os.path.splitext(descriptor.__file__)[0].split('/')[-1]
        return f'{descriptor_name}.{module_class.__name__}({s_params})'

    def gen_module_name(self, module: ModuleWidget, module_id: int):
        descriptor = module.module
        name = descriptor.name
        bad_characters = {'/', ' '}
        for c in bad_characters:
            name = name.replace(c, '_')
        return f'module_{module_id}_{name}'

    def method_params_to_str(self, params: Dict[str, Any]) -> str:
        s = []
        for name, value in params.items():
            if isinstance(value, str):
                s.append(f'{name}=\'{value}\'')
            else:
                s.append(f'{name}={value}')
        return ', '.join(s)
