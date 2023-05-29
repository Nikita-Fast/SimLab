
from code_gen.utils import ModuleWrapper, FlowGraph
import networkx as nx
from modules.general.Utils import ber_calculator
from modules.general.Generators import bin_gen
from modules.communication.Channels import awgn_descr
from modules.communication.Demodulators.QAM import qam_demod
from modules.communication.Modulators.QAM import qam_mod
id_to_module = dict()
id_to_descriptor = dict()

module_0_BERCalculator = ber_calculator.calc_ber
id_to_module[0] = module_0_BERCalculator
id_to_descriptor[0] = ber_calculator
module_1_BinaryGenerator = bin_gen.gen_binary_data
id_to_module[1] = module_1_BinaryGenerator
id_to_descriptor[1] = bin_gen
module_2_AWGNChannel = awgn_descr.AWGNChannel(information_bits_per_symbol=2, ebn0_db=12)
id_to_module[2] = module_2_AWGNChannel
id_to_descriptor[2] = awgn_descr
module_3_QAMDemodulator = qam_demod.QAMDemodulator(bits_per_symbol=2, constellation=None, mode='hard')
id_to_module[3] = module_3_QAMDemodulator
id_to_descriptor[3] = qam_demod
module_4_QAMModulator = qam_mod.QAMModulator(bits_per_symbol=2, constellation=None)
id_to_module[4] = module_4_QAMModulator
id_to_descriptor[4] = qam_mod

module_wrappers = []
for id, module in id_to_module.items():
	m = ModuleWrapper(id_to_descriptor[id], module, id)
	module_wrappers.append(m)

flow_graph = FlowGraph(modules=module_wrappers)
flow_graph.run()