
from code_gen.utils import ModuleWrapper
import networkx as nx
from modules.general import bin_gen
from modules.communication.Channels import awgn_descr
from modules.communication.Demodulators.QAM import qam_demod
from modules.communication.Modulators.QAM import qam_mod

connection_graph = nx.drawing.nx_pydot.read_dot('code_gen/connection_graph.dot')
id_to_module = dict()
id_to_descriptor = dict()

module_0_BinaryGenerator = bin_gen.gen_binary_data
id_to_module['0'] = module_0_BinaryGenerator
id_to_descriptor['0'] = bin_gen
module_1_AWGNChannel = awgn_descr.AWGNChannel(information_bits_per_symbol=4, ebn0_db=12)
id_to_module['1'] = module_1_AWGNChannel
id_to_descriptor['1'] = awgn_descr
module_2_QAMDemodulator = qam_demod.QAMDemodulator(bits_per_symbol=4, constellation=None, mode='hard')
id_to_module['2'] = module_2_QAMDemodulator
id_to_descriptor['2'] = qam_demod
module_3_QAMModulator = qam_mod.QAMModulator(bits_per_symbol=4, constellation=None)
id_to_module['3'] = module_3_QAMModulator
id_to_descriptor['3'] = qam_mod

id_to_module_wrapper = dict()
module_wrapper_to_id = dict()
for id, module in id_to_module.items():
	m = ModuleWrapper(id_to_descriptor[id], module, id)
	id_to_module_wrapper[id] = m
	module_wrapper_to_id[m] = id

sources = []
for module_wrapper in id_to_module_wrapper.values():
	if module_wrapper.is_source(connection_graph):
		sources.append(module_wrapper)

work_list = [*sources]
while work_list:
	module_wrapper = work_list[0]
	module_wrapper.execute()
	module_wrapper.send_to_successors(connection_graph, module_wrapper_to_id)
	work_list += module_wrapper.successors(connection_graph, id_to_module_wrapper)
	del(work_list[0])

sink_module_wrappers = [m for m in module_wrapper_to_id if m.is_sink(connection_graph)]
for m in sink_module_wrappers:
	print(f'module_id={m.get_id}, res={m.get_execution_results}')

print('EXECUTED')