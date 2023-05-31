import sys
sys.stdout.write('0')
from code_gen.utils import ModuleWrapper, FlowGraph
sys.stdout.write('1')
from modelling_utils.custom_exceptions import *
sys.stdout.write('2')
import sys
from modules.general.Utils import ebn0_db
sys.stdout.write('import of ebn0_db')
from modules.general.Utils import ber_calculator
sys.stdout.write('import of ber_calculator')
from modules.general.Utils import ber_plotter
sys.stdout.write('import of ber_plotter')
from modules.general.Generators import bin_gen
sys.stdout.write('import of bin_gen')
from modules.communication.Modulators.QAM import qam_mod
sys.stdout.write('import of qam_mod')
from modules.communication.Channels import awgn_descr
sys.stdout.write('import of awgn_descr')
from modules.communication.Demodulators.QAM import qam_demod
sys.stdout.write('import of qam_demod')


def f():
	sys.stdout.write('exec')
	bin_gen.bits_num = bin_gen.bits_num // 1
	sys.stdout.write(str(bin_gen.bits_num))
	
	id_to_module = dict()
	id_to_descriptor = dict()
	
	module_0_Eb_N0 = ebn0_db.EbN0dbModule(ebn0_db_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
	id_to_module[0] = module_0_Eb_N0
	id_to_descriptor[0] = ebn0_db
	module_1_BER_Calculator = ber_calculator.calc_ber
	id_to_module[1] = module_1_BER_Calculator
	id_to_descriptor[1] = ber_calculator
	module_2_BER_Plotter = ber_plotter.save
	id_to_module[2] = module_2_BER_Plotter
	id_to_descriptor[2] = ber_plotter
	module_3_Binary_Generator = bin_gen.gen_binary_data
	id_to_module[3] = module_3_Binary_Generator
	id_to_descriptor[3] = bin_gen
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
		m = ModuleWrapper(id_to_descriptor[id], module, id)
		module_wrappers.append(m)
	
	flow_graph = FlowGraph(modules=module_wrappers)
	while True:
		try:
			flow_graph.run()
		except SourceModuleRunOutOfDataException as e:
			flow_graph.execute_storage_modules()
			break

f()