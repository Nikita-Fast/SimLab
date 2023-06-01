import sys
from code_gen.utils import ModuleWrapper, FlowGraph
from modelling_utils.custom_exceptions import *
import sys
from modules.general.Generators import bin_gen
from modules.general.Utils import ebn0_db
from modules.general.Utils import ber_calculator
from modules.general.Utils import ber_plotter
from modules.communication.Modulators.QAM import qam_mod
from modules.communication.Channels import awgn_descr
from modules.communication.Demodulators.QAM import qam_demod


def f():
	id_to_module = dict()
	id_to_descriptor = dict()
	
	module_0_Binary_Generator = bin_gen.gen_binary_data
	id_to_module[0] = module_0_Binary_Generator
	id_to_descriptor[0] = bin_gen
	module_1_Eb_N0 = ebn0_db.EbN0dbModule(ebn0_db_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
	id_to_module[1] = module_1_Eb_N0
	id_to_descriptor[1] = ebn0_db
	module_2_BER_Calculator = ber_calculator.calc_ber
	id_to_module[2] = module_2_BER_Calculator
	id_to_descriptor[2] = ber_calculator
	module_3_BER_Plotter = ber_plotter.save
	id_to_module[3] = module_3_BER_Plotter
	id_to_descriptor[3] = ber_plotter
	module_4_QAM_Modulator = qam_mod.QAMModulator(bits_per_symbol=4, constellation=None)
	id_to_module[4] = module_4_QAM_Modulator
	id_to_descriptor[4] = qam_mod
	module_5_AWGNChannel = awgn_descr.AWGNChannel(information_bits_per_symbol=4)
	id_to_module[5] = module_5_AWGNChannel
	id_to_descriptor[5] = awgn_descr
	module_6_QAM_Demodulator = qam_demod.QAMDemodulator(bits_per_symbol=4, constellation=None, mode='hard')
	id_to_module[6] = module_6_QAM_Demodulator
	id_to_descriptor[6] = qam_demod
	
	module_wrappers = []
	for id, module in id_to_module.items():
		m = ModuleWrapper(id_to_descriptor[id], module, id, 1)
		module_wrappers.append(m)
	
	flow_graph = FlowGraph(modules=module_wrappers)
	while True:
		try:
			flow_graph.run()
		except SourceModuleRunOutOfDataException as e:
			flow_graph.execute_storage_modules()
			break

f()