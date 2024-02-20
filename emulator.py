def int32(x):
    full_range = 2 ** 8
    half_range = 2 ** 8 // 2
    unsigned = x + half_range           # go to unsinged
    wrapped = unsigned % full_range     # overflow/underflow
    signed = wrapped - half_range       # go back
    return signed

# print(int32(100))

# type Input = Callable

from typing import Callable

import logging
from functools import wraps    

# logging.setLevel(logging.DEBUG) 

do_log = False
log_depth = 0

def log(func):
    if not do_log:
        return func
    @wraps(func)
    def new_func(*args, **kwargs):
        global log_depth
        # saved_args = locals()
        res = '(no result due to an exception)'
        # try:
        if True:
            if do_log:
                tab = '    ' * log_depth
                # name = func.__qualname__
                name = (
                    func.__qualname__[0:3] + 
                    '.' + 
                    func.__name__
                )
                if func.__name__ == 'has_signal':
                    print(tab + name + ' ' + str(args[1]))
                else:
                    print(tab + name + ' ' + str((*args[1:],)))            
            log_depth += 1
            res = func(*args, **kwargs)
            if do_log:
                print(tab + '>> ' + str(res))
            log_depth -= 1
            return res
        # except Exception:
        #     raise
        # finally:
    return new_func        

class Input:
    source: Callable
    def __call__(self):
        return self.source()

class Multiplexer:
    input0: Input
    input1: Input
    sel: Input
    @log
    def output(self):
        sel = self.sel()
        if sel == 0:
            return self.input0()
        elif sel == 1:
            return self.input1()
        elif sel == 2:
            return self.input2()
        elif sel == 3:
            return self.input3()
        else:
            # assert False, 'Invalid `sel` for multiplexer'
            return None
    
class Register:
    _name: str = '' # for debugging
    input0: Input
    clock: Input
    latch: Input
    _value: any = None
    _last_input: any = None
    _latch: int = 0
    def __init__(self, initial_value = None):
        self._value = initial_value
    @log
    def simulate(self):
        _latch = self._latch
        latch = self.latch()
        clock = self.clock()
        # print(_latch, latch)
        # if _latch == 1 and latch == 0 and clock == 0:        
        if clock == 1 and latch == 1:
            self._latch = latch
            if self._value != self._last_input:
                self._value = self._last_input
                print(self._name + " register changed to %s" % (self._value))
        else:
            self._latch = latch
            input0 = self.input0()
            if input0 != self._last_input:
                self._last_input = input0
                # print(self._name + " register saved input: %s" % (self._last_input))
    @log
    def output(self):
        # self.simulate()
        return self._value
    
# r = Register(0)
# r._name = 'r'
# r.input0 = lambda: r.output() + 1
# r.latch = lambda: 0 #int(r.output() == 0)
# # r.clock = lambda: 0
# r.simulate()
# print(r.output())
# # r.clock = lambda: 1
# r.latch = lambda: 1 #int(r.output() == 0)
# r.simulate()
# print(r.output())
# exit(0)    

class ALU:
    input0: Input
    input1: Input
    sel: Input
    @log
    def output(self):
        if self.sel() == 0:
            return self.input0() + self.input1()
        elif self.sel() == 1:
            return self.input0() - self.input1()
    #todo: all other operations

class IsNegativeOp:    
    input0: Input
    @log
    def output(self):
        input0 = self.input0()
        if input0 is not None and input0 < 0:
            return 1
        else:
            return 0    
    
class IsZeroOp:
    input0: Input
    @log
    def output(self):
        input0 = self.input0()
        if input0 is not None and input0 == 0:
            return 1
        else:
            return 0
        
class IsPositiveOp:    
    input0: Input
    @log
    def output(self):
        input0 = self.input0()
        if input0 is not None and input0 > 0:
            return 1
        else:
            return 0        
            
class Memory:
    _name: str  # debug
    input0: Input = None
    address: Input
    read: Input
    write: Input
    clock: Input
    _contents: list
    _write: int = 1
    _last_input: any = None    
    def __init__(self, contents):
        self._contents = contents
    @log
    def simulate(self):
        _write = self._write
        write = self.write()
        clock = self.clock()
        if clock == 1 and write == 1:
            self._write = write
            value = self._last_input
            address = self.address()
            print(self._name + " memory cell %d changed to %s" % (address, value))        
            self._contents[address] = value
        else:
            self._write = write
            if self.input0 is not None:  # input is connected
                self._last_input = self.input0()
                # print(self._name + " memory saved input: %s" % (self._last_input))        
    @log
    def output(self):
        # self.simulate()
        if self.read() == 1:
            address = self.address()
            if self._name == 'MC_MEM':
                if address == 0:
                    value = self._contents[0]
                else:
                    value = self._contents[address[0]][address[1]]
            else:
                value = self._contents[address]
            # if self._name != 'MC_MEM':
                # print(self._name + ' read from memory at %d -> %s' % (address, value))
            return value
        else:
            # assert False, "Invalid memory read"
            return None

clk = 0        
def clock():
    return clk
        
    
# m = Memory([11, 22, 33])
# m._name = 'mem'
# m.input0 = lambda: 99
# m.write = lambda: 0
# # m.write = clock
# m.clock = clock
# m.address = lambda: 1
# m.read = lambda: 1
# m.simulate()
# print(m._contents, m.output())
# # clk += 1
# m.write = lambda: 1
# print()
# print(m._contents, m.output())
# exit(0)
        
class InputPort:
    input_buffer: list
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
    @log
    def output(self):
        self.input_buffer.pop(0)
        
class OutputPort:
    input0: Input
    _write: int = 0
    write: Input
    output_buffer: list
    def __init__(self, output_buffer):
        self.output_buffer = output_buffer
    @log
    def simulate(self):
        if self._write == 0 and self.write() == 1:
            self.ouput_buffer.append(self.input0())
        self._write = self.write()        
        
class DataPath:
    # external signals from ControlUnit
    instruction_arg: Input = Input()
    latch_data_address: Input = Input()
    data_address_sel: Input = Input()
    acc_sel: Input = Input()
    latch_acc: Input = Input()
    alu_operand_sel: Input = Input()
    alu_operation_sel: Input = Input()
    data_read: Input = Input()
    data_write: Input = Input()
    output_port_write: Input = Input()
    # internal components
    data_address_mux: Multiplexer
    data_address: Register
    data_memory: Memory
    input_port: InputPort
    acc_mux: Multiplexer
    acc: Register
    output_port: OutputPort
    alu_mux: Multiplexer
    alu: ALU
    is_zero_op: IsZeroOp
    is_negative_op: IsNegativeOp
    def __init__(self, data_memory, input_buffer, output_buffer, clock): 
        self.data_address_mux = Multiplexer()
        self.data_address = Register(0)
        self.data_memory = Memory(data_memory)
        self.acc_mux = Multiplexer()
        self.acc = Register(0)
        self.alu_mux = Multiplexer()
        self.alu = ALU()
        self.is_negative_op = IsNegativeOp()
        self.is_zero_op = IsZeroOp()
        self.is_positive_op = IsPositiveOp()
        self.input_port = InputPort(input_buffer)
        self.output_port = OutputPort(output_buffer)        

        self.data_address_mux.input0 = self.instruction_arg
        self.data_address_mux.input1 = self.data_memory.output
        self.data_address_mux.sel = self.data_address_sel       
        
        self.data_address.input0 = self.data_address_mux.output
        self.data_address.latch = self.latch_data_address        
        self.data_address.clock = clock
        
        self.data_memory.input0 = self.acc.output   
        self.data_memory.read = self.data_read
        self.data_memory.write = self.data_write
        self.data_memory.address = self.data_address.output        
        self.data_memory.clock = clock
        
        self.acc_mux.input0 = self.instruction_arg
        self.acc_mux.input1 = self.input_port.output
        self.acc_mux.input2 = self.data_memory.output
        self.acc_mux.input3 = self.alu.output
        self.acc_mux.sel = self.acc_sel        
        
        self.acc.input0 = self.acc_mux.output
        self.acc.latch = self.latch_acc        
        self.acc.clock = clock
        
        self.alu_mux.input0 = self.data_memory.output
        self.alu_mux.input1 = self.instruction_arg
        self.alu_mux.sel = self.alu_operand_sel
        
        self.alu.input0 = self.acc.output
        self.alu.input1 = self.alu_mux.output
        self.alu.sel = self.alu_operation_sel        
        
        self.is_negative_op.input0 = self.acc.output
        self.is_zero_op.input0 = self.acc.output        
        self.is_positive_op.input0 = self.acc.output
        
        self.output_port.input0 = self.acc.output
        self.output_port.write = self.output_port_write
    @log
    def simulate(self):
        self.data_address.simulate()
        self.data_memory.simulate()       
        self.acc.simulate()
        pass
    # outgoing signals
    @log
    def negative_flag(self):        
        return self.is_negative_op.output()
    @log
    def zero_flag(self):
        return self.is_zero_op.output()
    @log
    def positive_flag(self):        
        return self.is_positive_op.output()    

# dp = DataPath([11, 0, 33, 44], [], [])
# #                  ^^
# dp.data_address_sel = 0
# dp.simulate()
# dp.instruction_arg = 1
# dp.simulate()
# dp.latch_data_address = 1
# dp.simulate()
# dp.data_read = 1
# dp.simulate()
# dp.acc_sel = 2
# dp.simulate()
# dp.latch_acc = 1
# dp.simulate()
# print(dp.acc.output)
# print(dp.zero_flag)
# print(dp.negative_flag)

class IncrementOp:     
    input0: Input
    @log
    def output(self):
        return self.input0() + 1

class AndGate:     
    input0: Input
    input1: Input
    @log
    def output(self):
        if self.input0() == 1 and self.input1() == 1:
            return 1
        else:
            return 0
    
class OrGate:     
    input0: Input
    input1: Input
    input2: Input
    @log
    def output(self):
        if self.input0() == 1 or self.input1() == 1 or self.input2():
            return 1
        else:
            return 0

from enum import Enum    #todo: move to the beginning of the machine file
from enum import Flag, global_enum

@global_enum
class Signal(Flag):
    NONE = 0
    DATA_ADDRESS_SEL__ARG = 2 ** 0
    DATA_ADDRESS_SEL__DATA_OUT = 2 ** 1
    LATCH_DATA_ADDRESS = 2 ** 2
    ACC_SEL__ARG = 2 ** 3
    ACC_SEL__INPUT_PORT = 2 ** 4
    ACC_SEL__DATA_OUT = 2 ** 5
    ACC_SEL__ALU = 2 ** 6
    LATCH_ACC = 2 ** 7
    ALU_OPERAND_SEL__DATA_OUT = 2 ** 8
    ALU_OPERAND_SEL__ARG = 2 ** 9
    ALU_OPERATION_SEL__ADD = 2 ** 10
    ALU_OPERATION_SEL__SUB = 2 ** 11
    ALU_OPERATION_SEL__MUL = 2 ** 12
    ALU_OPERATION_SEL__DIV = 2 ** 13
    ALU_OPERATION_SEL__MOD = 2 ** 14
    DATA_READ = 2 ** 15
    DATA_WRITE = 2 ** 16
    INPUT_PORT_READ = 2 ** 17
    OUTPUT_PORT_WRITE = 2 ** 18
    PC_SEL__ARG = 2 ** 19
    PC_SEL__NEXT = 2 ** 20
    LATCH_PC = 2 ** 21
    MPC_SEL__FETCH = 2 ** 29
    MPC_SEL__NEW = 2 ** 22
    MPC_SEL__NEXT = 2 ** 23
    LATCH_MPC = 2 ** 24
    JUMP_IF_NEGATIVE = 2 ** 25
    JUMP_IF_ZERO = 2 ** 26
    JUMP_IF_POSITIVE = 2 ** 27
    HALT = 2 ** 28

class InstructionDecoder:
    input0: Input
    @log
    def micro_code_address(self):
        instruction = self.input0()
        opcode_name = instruction['opcode']
        arg_type = instruction['arg_type']
        address = [arg_type, opcode_name]
        # print('instruction decoded -> %s' % (address)), 
        return address
        # opcode_names = [
        #     'ld', 'st',
        #     'add', 'sub', 'mul', 'div', 'mod', 
        #     'cmp',
        #     'jmp', 'je', 'jne', 'jg', 'jl', 'jge', 'jle',
        #     'hlt'
        # ]
        # arg_type_codes = {
        #     'immediate': 0,
        #     'address': 1,
        #     'indirect_address': 2,
        #     'none': 0
        # }
        # arg_type_code = arg_type_codes[arg_type]
        # address = (opcode_names.index(opcode_name) + arg_type_code * 20) * 3
        # print("IDEC:", opcode_name, arg_type, arg_type_code, opcode_names.index(opcode_name), "->", address)
        # return address
    @log
    def instruction_arg(self):
        return self.input0()['arg']

class ControlUnit:
    data_path: DataPath
    program_counter_mux: Multiplexer
    program_counter: Register
    increment_pc: IncrementOp
    code_memory: Memory
    instruction_decoder: InstructionDecoder
    micro_program_counter_mux: Multiplexer
    micro_program_counter: Register
    increment_mpc: IncrementOp
    micro_code_memory: Memory
    # control_word: Register
    negative_jump_and: AndGate
    zero_jump_and: AndGate
    positive_jump_and: AndGate
    jump_or: OrGate
    def __init__(self, data_path, instructions, microcode, clock):
        
        self.data_path = data_path
        self.program_counter_mux = Multiplexer()
        self.program_counter = Register(0)
        self.increment_pc = IncrementOp()
        self.code_memory = Memory(instructions)
        self.instruction_decoder = InstructionDecoder()
        self.micro_program_counter_mux = Multiplexer()
        self.micro_program_counter = Register(0)
        self.increment_mpc = IncrementOp()
        self.micro_code_memory = Memory(microcode)
        # self.control_word = Register(Signal(0))
        self.negative_jump_and = AndGate()
        self.zero_jump_and = AndGate()
        self.positive_jump_and = AndGate()
        self.jump_or = OrGate()        
        data_path.instruction_arg.source = self.instruction_arg
        data_path.latch_data_address.source = self.latch_data_address
        data_path.data_address_sel.source = self.data_address_sel
        data_path.acc_sel.source = self.acc_sel
        data_path.latch_acc.source = self.latch_acc
        data_path.alu_operand_sel.source = self.alu_operand_sel
        data_path.alu_operation_sel.source = self.alu_operation_sel
        data_path.data_read.source = self.data_read
        data_path.data_write.source = self.data_write
        data_path.output_port_write.source = self.output_port_write
        
        self.program_counter_mux.input0 = self.increment_pc.output
        self.program_counter_mux.input1 = self.instruction_arg
        self.program_counter_mux.sel = self.jump_or.output        
        
        self.program_counter.input0 = self.program_counter_mux.output
        self.program_counter.latch = self.latch_pc
        self.program_counter.clock = clock
        
        self.increment_pc.input0 = self.program_counter.output        
        
        self.code_memory.address = self.program_counter.output   
        self.code_memory.read = lambda: 1
        self.code_memory.write = lambda: 0
        self.code_memory.clock = clock
        
        self.instruction_decoder.input0 = self.code_memory.output
        
        self.micro_program_counter_mux.input0 = lambda: 0
        self.micro_program_counter_mux.input1 = self.instruction_micro_code_address
        self.micro_program_counter_mux.input2 = self.increment_mpc.output
        self.micro_program_counter_mux.sel = self.mpc_sel        
        
        self.micro_program_counter.input0 = self.micro_program_counter_mux.output
        self.micro_program_counter.latch = self.latch_mpc      
        self.micro_program_counter.clock = clock
        
        self.increment_mpc.input0 = self.micro_program_counter.output         

        self.micro_code_memory.address = self.micro_program_counter.output
        self.micro_code_memory.read = lambda: 1
        self.micro_code_memory.write = lambda: 0
        self.micro_code_memory.clock = clock
        
        # self.control_word.input0 = self.micro_code_memory.output
        # self.control_word.latch = lambda: 1 - clock()

        self.negative_jump_and.input0 = self.jump_if_negative
        self.negative_jump_and.input1 = self.data_path.negative_flag
        
        self.zero_jump_and.input0 = self.jump_if_zero        
        self.zero_jump_and.input1 = self.data_path.zero_flag
        
        self.positive_jump_and.input0 = self.jump_if_positive        
        self.positive_jump_and.input1 = self.data_path.positive_flag
        
        self.jump_or.input0 = self.negative_jump_and.output        
        self.jump_or.input1 = self.zero_jump_and.output
        self.jump_or.input2 = self.positive_jump_and.output        

    @log
    def simulate(self):
        self.data_path.simulate()
        self.program_counter.simulate()
        self.code_memory.simulate()
        self.micro_program_counter.simulate()
        self.micro_code_memory.simulate()
        ## self.control_word.simulate()
        pass
    # instruction decoder signals
    @log
    def instruction_micro_code_address(self):
        return self.instruction_decoder.micro_code_address()
    @log
    def instruction_arg(self):
        return self.instruction_decoder.instruction_arg()    
    # internal and outgoing signals
    @log
    def has_signal(self, signal):
        signals = self.micro_code_memory.output()
        # if signal in self.control_word.output():
        if signal in signals:
            return 1
        else:
            return 0
    # outgoing signals    
    @log
    def data_address_sel(self):
        if self.has_signal(Signal.DATA_ADDRESS_SEL__ARG):
            return 0
        elif self.has_signal(Signal.DATA_ADDRESS_SEL__DATA_OUT):
            return 1
        else:
            return None
            # assert False, "Invalid data_address MUX selector"
    @log
    def latch_data_address(self):
        return self.has_signal(Signal.LATCH_DATA_ADDRESS)
    @log
    def acc_sel(self):
        if self.has_signal(Signal.ACC_SEL__ARG):
            return 0
        elif self.has_signal(Signal.ACC_SEL__INPUT_PORT):
            return 1
        elif self.has_signal(Signal.ACC_SEL__DATA_OUT):
            return 2
        elif self.has_signal(Signal.ACC_SEL__ALU):
            return 3
        else:
            return None
            # assert False, "Invalid ACC MUX selector"        
    @log 
    def latch_acc(self):
        return self.has_signal(Signal.LATCH_ACC)
    @log
    def alu_operand_sel(self):
        if self.has_signal(Signal.ALU_OPERAND_SEL__DATA_OUT):
            return 0
        elif self.has_signal(Signal.ALU_OPERAND_SEL__ARG):
            return 1
        else:
            return None
            # assert False, "Invalid ALU operand selector"   
    @log
    def alu_operation_sel(self):
        if self.has_signal(Signal.ALU_OPERATION_SEL__ADD):
            return 0
        elif self.has_signal(Signal.ALU_OPERATION_SEL__SUB):
            return 1
        elif self.has_signal(Signal.ALU_OPERATION_SEL__MUL):
            return 2
        elif self.has_signal(Signal.ALU_OPERATION_SEL__DIV):
            return 3
        elif self.has_signal(Signal.ALU_OPERATION_SEL__MOD):
            return 4
        else:
            return None
            # assert False, "Invalid ALU operation selector"     
    @log
    def data_read(self):
        return self.has_signal(Signal.DATA_READ)
    @log
    def data_write(self):
        return self.has_signal(Signal.DATA_WRITE)    
    @log
    def output_port_write(self):
        return self.has_signal(Signal.OUTPUT_PORT_WRITE)
    # internal signals
    @log
    def latch_pc(self):
        return self.has_signal(Signal.LATCH_PC) 
    @log
    def mpc_sel(self):
        if self.has_signal(Signal.MPC_SEL__FETCH):
            return 0
        if self.has_signal(Signal.MPC_SEL__NEW):
            return 1
        elif self.has_signal(Signal.MPC_SEL__NEXT):
            return 2
        else:
            return None
            # assert False, "Invalid mPC MUX selector"
    @log
    def latch_mpc(self):
        return self.has_signal(Signal.LATCH_MPC) 
    @log
    def jump_if_negative(self):
        return self.has_signal(Signal.JUMP_IF_NEGATIVE)
    @log
    def jump_if_zero(self):
        return self.has_signal(Signal.JUMP_IF_ZERO)
    @log
    def jump_if_positive(self):
        return self.has_signal(Signal.JUMP_IF_POSITIVE)
        
        
do_log = True
def execute(instructions, data, input_buffer):
    clock_value = 0
    
    # @log
    def clock():
        return clock_value
    
    output_buffer = []
    dp = DataPath(data, input_buffer, output_buffer, clock)
    
    # debug
    dp.data_address._name = 'DA'
    dp.acc._name = 'ACC'
    dp.data_memory._name = 'D_MEM'
    
    # print(instructions)
    cu = ControlUnit(dp, instructions, {
        # 0: LATCH_PC | MPC_SEL__NEW | LATCH_MPC,
        0: MPC_SEL__NEW | LATCH_MPC,
        'address': {
            'jmp': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_NEGATIVE | JUMP_IF_ZERO | JUMP_IF_POSITIVE,
            'je': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_ZERO,
            'jne': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_NEGATIVE | JUMP_IF_POSITIVE,
            'jg': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_POSITIVE,
            'jl': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_NEGATIVE,
            'jge': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_POSITIVE | JUMP_IF_ZERO,
            'jle': LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | JUMP_IF_NEGATIVE | JUMP_IF_ZERO,
        },
        'immediate': {
            'ld': ACC_SEL__ARG | LATCH_ACC | PC_SEL__NEXT | LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
            'add': (
                ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__ADD |
                ACC_SEL__ALU | LATCH_ACC |
                PC_SEL__NEXT | LATCH_PC | 
                MPC_SEL__FETCH | LATCH_MPC
            ),
            #todo: sub, mul, div, mod
        },
        'none': {
            'hlt': HALT
        }
        # ,
        # *([Signal.MPC_SEL__NEXT] * 83),
        # # immediate
        # Signal.PC_SEL__ARG | Signal.LATCH_PC | Signal.MPC_SEL__NEW | Signal.LATCH_MPC,
        # # Signal.ACC_SEL__ARG | Signal.LATCH_ACC | 
        # # Signal.MPC_SEL__NEXT | Signal.LATCH_MPC,
        # # Signal.ACC_SEL__ARG | Signal.LATCH_ACC | Signal.MPC_SEL__NEXT,
        # Signal.MPC_SEL__NEXT,
        # Signal.HALT,
        # Signal.NONE,
        # Signal.PC_SEL__ARG | Signal.LATCH_PC,
        # Signal.PC_SEL__ARG | Signal.LATCH_PC,
        # Signal.ACC_SEL__ARG | Signal.LATCH_ACC,
        # Signal.MPC_SEL__NEXT,
        # *([Signal.MPC_SEL__NEXT] * 1000),
        # # Signal.MPC_SEL__NEXT,
        # # Signal.MPC_SEL__NEXT,
        # Signal.NONE, # special
        # # address
        # # indirect_address ?
    }, clock)

    # debug
    cu.program_counter._name = 'PC'
    cu.micro_program_counter._name = 'mPC'
    # cu.control_word._name = 'CW'
    cu.code_memory._name = 'C_MEM'
    cu.micro_code_memory._name = 'MC_MEM'
    
    ticks = 0
    half_ticks = 0
    
    def half_tick():
        nonlocal clock_value, half_ticks
        # print("half_tick %d  clock %d" % (half_ticks, clock_value))
        # print( cu.micro_code_memory.output(), dp.negative_flag(), dp.zero_flag(), dp.positive_flag() )
        cu.simulate()
        # print( cu.micro_code_memory.output(), dp.negative_flag(), dp.zero_flag(), dp.positive_flag() )
        clock_value = 1 - clock_value
        # print()       
        half_ticks += 1
        
    def tick():
        nonlocal ticks
        half_tick()
        half_tick()
        opcode = cu.code_memory.output()['opcode'].upper()
        arg_type = cu.code_memory.output()['arg_type']
        raw_arg = cu.code_memory.output().get('arg', '')
        if arg_type == 'immediate' or opcode.startswith('J'):
            arg_repr = '%s' % raw_arg
        elif arg_type == 'address':
            arg_repr = '[%s]' % raw_arg
        elif arg_type == 'indirect_address':
            arg_repr = '[[%s]]' % raw_arg
        else:
            arg_repr = ''
        print("\ntick %s  PC %s  mPC %s  ACC %s  DA %s  DOUT %s  %s   MC: %s" % (
            ticks + 1,
            cu.program_counter.output(),
            cu.micro_program_counter.output(),
            cu.data_path.acc.output(),
            cu.data_path.data_address.output(),
            cu.data_path.data_memory.output(),
            '%s %s' % (opcode, arg_repr),
            cu.micro_code_memory.output(),
        ))                
        ticks += 1
        if cu.has_signal(Signal.HALT):
            print('simulation terminated')
            exit(0)        
        # print('---------------------------------')
    
    tick()
    tick()
    
    tick()
    tick()
    
    tick()
    tick()
    
    tick()
    tick()

lines = []
while True:
    try:
        line = input()
        if line and line != '###':
            lines.append(line)
        else:
            break
    except:
        break
text = '\n'.join(lines)
instructions = json.loads(text)
execute(instructions, [-11, -22, -33, -44], [])    
# execute(program['instructions'], program['data'], [])    

"""
print(output)
print(program['data'])
"""