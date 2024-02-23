import sys
import json
from typing import Callable

# wraparound numbers to emulate 32-bit machine
def int32(x):
    x = int(x)
    full_range = 2 ** 32
    half_range = 2 ** 32 // 2
    unsigned = x + half_range           # go to unsinged
    wrapped = unsigned % full_range     # overflow/underflow
    signed = wrapped - half_range       # go back
    return signed

Input = Callable

class Multiplexer:
    input0: Input
    input1: Input
    sel: Input
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
    
class Register:
    input0: Input
    latch: Input
    clock: Input
    _value: any = None
    _last_input: any = None  # last value seen before latch
    def __init__(self, initial_value):
        self._value = initial_value
    def simulate(self):
        if self.clock() == 1 and self.latch() == 1:
            self._value = self._last_input
        else:
            self._last_input = self.input0()
    def output(self):
        return self._value
    
class ALU:
    input0: Input
    input1: Input
    sel: Input
    def output(self):
        if self.sel() == 0:
            return int32(self.input0() + self.input1())
        elif self.sel() == 1:
            return int32(self.input0() - self.input1())
        elif self.sel() == 2:
            return int32(self.input0() * self.input1())
        elif self.sel() == 3:
            return int32(self.input0() / self.input1())
        elif self.sel() == 4:
            return int32(self.input0() % self.input1())

class Memory:
    input0: Input 
    address: Input
    read: Input
    write: Input
    clock: Input
    _contents: list
    _last_input: any = None    
    def __init__(self, contents):
        self._contents = contents
    def simulate(self):
        if self.clock() == 1 and self.write() == 1:
            address = self.address()
            self._contents[address] = self._last_input
        else:
            self._last_input = self.input0()
    def output(self):
        if self.read() == 1:
            address = self.address()
            return self._contents[address]
        
class InputPort:
    read: Input
    clock: Input
    input_buffer: list
    _last_value: any = None  # last read value
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
    def output(self):
        if self.clock() == 1 and self.read() == 1:
            if self.input_buffer:
                self._last_value = self.input_buffer.pop(0)
                return self._last_value
            else:
                raise EOFError
        else:
            return self._last_value        
        
class OutputPort:
    input0: Input
    write: Input
    clock: Input
    _last_input: any = None  # last seen input before write
    output_buffer: list
    def __init__(self, output_buffer):
        self.output_buffer = output_buffer
    def simulate(self):
        if self.clock() == 1 and self.write() == 1:
            value = self.input0()
            self.output_buffer.append(value)
        else:
            self._last_input = self.input0()
        
class DataPath:
    # external signals from ControlUnit
    instruction_arg: Input 
    latch_data_address: Input 
    data_address_sel: Input 
    acc_sel: Input 
    latch_acc: Input 
    alu_operand_sel: Input 
    alu_operation_sel: Input 
    data_read: Input 
    data_write: Input 
    input_port_read: Input 
    output_port_write: Input 
    clock: Input 
    # internal components
    data_address_mux: Multiplexer
    data_address: Register
    data_memory: Memory
    alu_mux: Multiplexer
    alu: ALU
    acc_mux: Multiplexer
    acc: Register
    input_port: InputPort
    output_port: OutputPort
    def __init__(self, data_memory, input_buffer, output_buffer): 
        self.data_address_mux = Multiplexer()
        self.data_address = Register(0)
        self.data_memory = Memory(data_memory)
        self.acc_mux = Multiplexer()
        self.acc = Register(0)
        self.alu_mux = Multiplexer()
        self.alu = ALU()
        self.input_port = InputPort(input_buffer)
        self.output_port = OutputPort(output_buffer)   
    def interconnect_components(self):
        self.data_address_mux.input0 = self.instruction_arg
        self.data_address_mux.input1 = self.data_memory.output
        self.data_address_mux.sel = self.data_address_sel       
        
        self.data_address.input0 = self.data_address_mux.output
        self.data_address.latch = self.latch_data_address        
        self.data_address.clock = self.clock
        
        self.data_memory.input0 = self.acc.output   
        self.data_memory.read = self.data_read
        self.data_memory.write = self.data_write
        self.data_memory.address = self.data_address.output        
        self.data_memory.clock = self.clock
        
        self.acc_mux.input0 = self.instruction_arg
        self.acc_mux.input1 = self.input_port.output
        self.acc_mux.input2 = self.data_memory.output
        self.acc_mux.input3 = self.alu.output
        self.acc_mux.sel = self.acc_sel        
        
        self.acc.input0 = self.acc_mux.output
        self.acc.latch = self.latch_acc        
        self.acc.clock = self.clock
        
        self.alu_mux.input0 = self.data_memory.output
        self.alu_mux.input1 = self.instruction_arg
        self.alu_mux.sel = self.alu_operand_sel
        
        self.alu.input0 = self.acc.output
        self.alu.input1 = self.alu_mux.output
        self.alu.sel = self.alu_operation_sel        
        
        self.input_port.read = self.input_port_read
        self.input_port.clock = self.clock
        
        self.output_port.input0 = self.acc.output
        self.output_port.clock = self.clock
        self.output_port.write = self.output_port_write
    def simulate(self):
        self.data_address.simulate()
        self.data_memory.simulate()       
        self.acc.simulate()
        self.output_port.simulate()
    # outgoing signals
    def negative_flag(self):        
        acc = self.acc.output()
        return acc is not None and acc < 0
    def zero_flag(self):
        acc = self.acc.output()
        return acc is not None and acc == 0
    def positive_flag(self):        
        acc = self.acc.output()
        return acc is not None and acc > 0

from enum import Enum    #todo: move to the beginning of the machine file
from enum import Flag, global_enum

DA_SEL__ARG = 2 ** 0
DA_SEL__DATA_OUT = 2 ** 1
LATCH_DA = 2 ** 2
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
# PC_SEL__ARG = 2 ** 19
# PC_SEL__NEXT = 2 ** 20
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
    # opcode + arg_type -> microcode memory address
    instruction_map = {
        'immediate': {
            'ld': 1, 'add': 2, 'sub': 3, 
            'mul': 4, 'div': 5, 'mod': 6,
        },
        'address': {
            'ld': 7, 'st': 9, 'add': 11, 
            'sub': 13, 'mul': 15, 'div': 17,
            'mod': 19, 'jmp': 21, 'je': 22,
            'jne': 23, 'jg': 24, 'jl': 25,
            'jge': 26, 'jle': 27, 'in': 28,
            'out': 30,
        },
        'indirect_address': {
            'ld': 31, 'st': 35,
        },
        'none': {
            'hlt': 38
        }
    }    
    def micro_code_address(self):
        instruction = self.input0()
        opcode_name = instruction['opcode']
        arg_type = instruction['arg_type']
        address = self.instruction_map[arg_type][opcode_name]
        return address
    def instruction_arg(self):
        return self.input0()['arg']

class ControlUnit:
    # external signals
    clock: Input 
    # internal components
    dp: DataPath
    pc_mux: Multiplexer
    pc: Register
    code_memory: Memory
    instruction_decoder: InstructionDecoder
    mpc_mux: Multiplexer
    mpc: Register
    micro_code_memory: Memory
    def __init__(self, dp, instructions, microcode):
        self.dp = dp
        self.pc_mux = Multiplexer()
        self.pc = Register(0)
        self.code_memory = Memory(instructions)
        self.instruction_decoder = InstructionDecoder()
        self.mpc_mux = Multiplexer()
        self.mpc = Register(0)
        self.micro_code_memory = Memory(microcode)
    def interconnect_components(self):
        self.pc_mux.input0 = lambda: self.pc.output() + 1
        self.pc_mux.input1 = self.instruction_arg
        self.pc_mux.sel = self.should_jump
        
        self.pc.input0 = self.pc_mux.output
        self.pc.latch = self.latch_pc
        self.pc.clock = self.clock
        
        self.code_memory.input0 = lambda: None
        self.code_memory.address = self.pc.output   
        self.code_memory.read = lambda: 1
        self.code_memory.write = lambda: 0
        self.code_memory.clock = self.clock
        
        self.instruction_decoder.input0 = self.code_memory.output
        
        self.mpc_mux.input0 = lambda: 0
        self.mpc_mux.input1 = self.instruction_decoder.micro_code_address
        self.mpc_mux.input2 = lambda: self.mpc.output() + 1
        self.mpc_mux.sel = self.mpc_sel        
        
        self.mpc.input0 = self.mpc_mux.output
        self.mpc.latch = self.latch_mpc      
        self.mpc.clock = self.clock

        self.micro_code_memory.input0 = lambda: None
        self.micro_code_memory.address = self.mpc.output
        self.micro_code_memory.read = lambda: 1
        self.micro_code_memory.write = lambda: 0
        self.micro_code_memory.clock = self.clock
    def simulate(self):
        self.dp.simulate()
        self.pc.simulate()
        self.code_memory.simulate()
        self.mpc.simulate()
        self.micro_code_memory.simulate()
    # instruction decoder signals exposed for Data Path
    def instruction_micro_code_address(self):
        return self.instruction_decoder.micro_code_address()
    def instruction_arg(self):
        return self.instruction_decoder.instruction_arg()    
    # helper function for signal checks
    def has_signal(self, signal):
        signals = self.micro_code_memory.output()
        return (signals & signal) == signal
    # outgoing signals    
    def data_address_sel(self):
        if self.has_signal(DA_SEL__ARG):
            return 0
        elif self.has_signal(DA_SEL__DATA_OUT):
            return 1
    def latch_data_address(self):
        return self.has_signal(LATCH_DA)
    def acc_sel(self):
        if self.has_signal(ACC_SEL__ARG):
            return 0
        elif self.has_signal(ACC_SEL__INPUT_PORT):
            return 1
        elif self.has_signal(ACC_SEL__DATA_OUT):
            return 2
        elif self.has_signal(ACC_SEL__ALU):
            return 3
    def latch_acc(self):
        return self.has_signal(LATCH_ACC)
    def alu_operand_sel(self):
        if self.has_signal(ALU_OPERAND_SEL__DATA_OUT):
            return 0
        elif self.has_signal(ALU_OPERAND_SEL__ARG):
            return 1
    def alu_operation_sel(self):
        if self.has_signal(ALU_OPERATION_SEL__ADD):
            return 0
        elif self.has_signal(ALU_OPERATION_SEL__SUB):
            return 1
        elif self.has_signal(ALU_OPERATION_SEL__MUL):
            return 2
        elif self.has_signal(ALU_OPERATION_SEL__DIV):
            return 3
        elif self.has_signal(ALU_OPERATION_SEL__MOD):
            return 4
    def data_read(self):
        return self.has_signal(DATA_READ)
    def data_write(self):
        return self.has_signal(DATA_WRITE)    
    def input_port_read(self):
        return self.has_signal(INPUT_PORT_READ)
    def output_port_write(self):
        return self.has_signal(OUTPUT_PORT_WRITE)
    # internal signals
    def latch_pc(self):
        return self.has_signal(LATCH_PC) 
    def mpc_sel(self):
        if self.has_signal(MPC_SEL__FETCH):
            return 0
        if self.has_signal(MPC_SEL__NEW):
            return 1
        elif self.has_signal(MPC_SEL__NEXT):
            return 2
    def latch_mpc(self):
        return self.has_signal(LATCH_MPC) 
    def jump_if_negative(self):
        return self.has_signal(JUMP_IF_NEGATIVE)
    def jump_if_zero(self):
        return self.has_signal(JUMP_IF_ZERO)
    def jump_if_positive(self):
        return self.has_signal(JUMP_IF_POSITIVE)
    def should_jump(self):
        cu, dp = self, self.dp
        jl = cu.jump_if_negative() == 1 and dp.negative_flag() == 1
        je = cu.jump_if_zero() == 1 and dp.zero_flag() == 1
        jg = cu.jump_if_positive() == 1 and dp.positive_flag() == 1
        return jl == 1 or je == 1 or jg == 1       

MICROCODE = [
    MPC_SEL__NEW | LATCH_MPC, # fetch microcode
    # all immediate argument instructions:
    # ld
    ACC_SEL__ARG | LATCH_ACC | 
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # add
    ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__ADD |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # sub
    ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__SUB |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # mul 
    ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__MUL |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # div
    ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__DIV |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # mod
    ALU_OPERAND_SEL__ARG | ALU_OPERATION_SEL__MOD |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # all instructions with address argument:
    # ld 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | ACC_SEL__DATA_OUT | LATCH_ACC | 
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # st
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC, 
    DATA_WRITE | LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # add
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | 
    ALU_OPERAND_SEL__DATA_OUT | ALU_OPERATION_SEL__ADD |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,          
    # sub 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | 
    ALU_OPERAND_SEL__DATA_OUT | ALU_OPERATION_SEL__SUB |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,          
    # mul 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | 
    ALU_OPERAND_SEL__DATA_OUT | ALU_OPERATION_SEL__MUL |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,      
    # div 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | 
    ALU_OPERAND_SEL__DATA_OUT | ALU_OPERATION_SEL__DIV |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # mod 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | 
    ALU_OPERAND_SEL__DATA_OUT | ALU_OPERATION_SEL__MOD |
    ACC_SEL__ALU | LATCH_ACC |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # jmp
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_NEGATIVE | JUMP_IF_ZERO | JUMP_IF_POSITIVE,
    # je
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_ZERO,
    # jne
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_NEGATIVE | JUMP_IF_POSITIVE,
    # jg
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_POSITIVE,
    # jl 
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_NEGATIVE,
    # jge
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_POSITIVE | JUMP_IF_ZERO,
    # jle 
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC | 
    JUMP_IF_NEGATIVE | JUMP_IF_ZERO,
    # in
    INPUT_PORT_READ | ACC_SEL__INPUT_PORT |
    MPC_SEL__NEXT | LATCH_MPC,
    ACC_SEL__INPUT_PORT | LATCH_ACC | 
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # out
    OUTPUT_PORT_WRITE |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # all instructions with indirect_address argument:
    # ld
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | DA_SEL__DATA_OUT | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | ACC_SEL__DATA_OUT | LATCH_ACC | MPC_SEL__NEXT | LATCH_MPC,
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # st 
    DA_SEL__ARG | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_READ | DA_SEL__DATA_OUT | LATCH_DA | MPC_SEL__NEXT | LATCH_MPC,
    DATA_WRITE |
    LATCH_PC | MPC_SEL__FETCH | LATCH_MPC,
    # other instructions:
    # hlt
    HALT
]

class Machine:
    dp: DataPath
    cu: ControlUnit
    _clock: int = 0
    def __init__(self, data, input_buffer, output_buffer, 
                 instructions, microcode):
        self.dp = DataPath(data, input_buffer, output_buffer)
        self.cu = ControlUnit(self.dp, instructions, microcode)
    def interconnect_components(self):
        dp, cu = self.dp, self.cu
        dp.instruction_arg = cu.instruction_arg
        dp.latch_data_address = cu.latch_data_address
        dp.data_address_sel = cu.data_address_sel
        dp.acc_sel = cu.acc_sel
        dp.latch_acc = cu.latch_acc
        dp.alu_operand_sel = cu.alu_operand_sel
        dp.alu_operation_sel = cu.alu_operation_sel
        dp.data_read = cu.data_read
        dp.data_write = cu.data_write
        dp.input_port_read = cu.input_port_read
        dp.output_port_write = cu.output_port_write
        dp.clock = self.clock    
        dp.interconnect_components()
        cu.clock = self.clock
        cu.interconnect_components()        
    def simulate(self):
        self.cu.simulate()
        self._clock = 1 - self._clock
    def clock(self):
        return self._clock
    
def print_status(ticks, dp, cu):
    opcode = cu.code_memory.output()['opcode']
    arg_type = cu.code_memory.output()['arg_type']
    raw_arg = cu.code_memory.output().get('arg', '')
    if arg_type == 'immediate' or opcode.startswith('j') or opcode in ['in', 'out']:
        arg_repr = '%s' % raw_arg
    elif arg_type == 'address':
        arg_repr = '[%s]' % raw_arg
    elif arg_type == 'indirect_address':
        arg_repr = '[[%s]]' % raw_arg
    else:
        arg_repr = ''
    print("tick #%s: PC=%s MPC=%s ACC=%s DA=%s DOUT=%s  %s\ninput=%s output=%s" % (
        ticks + 1,
        cu.pc.output(),
        cu.mpc.output(),
        cu.dp.acc.output(),
        cu.dp.data_address.output(),
        cu.dp.data_memory.output(),
        '%s %s' % (opcode.upper(), arg_repr),
        list(map(chr, dp.input_port.input_buffer)),
        list(map(chr, dp.output_port.output_buffer))
    ))    

def simulate(instructions, data, input_buffer):
    output_buffer = []    
    machine = Machine(data, input_buffer, output_buffer, instructions, MICROCODE)
    machine.interconnect_components()
    dp, cu = machine.dp, machine.cu
    instrs = 0
    ticks = 0            
    try:
        while True:
            if cu.has_signal(MPC_SEL__NEW):
                instrs += 1
            # low level clock - gather information
            machine.simulate()
            # high level clock - read/write information
            machine.simulate()
            # print_status(ticks, dp, cu)        
            ticks += 1
            if cu.has_signal(HALT):
                raise StopIteration
    except EOFError:
        print('end of input - simulation terminated')
    except StopIteration:
        print('simulation terminated')

    print('instructions executed: %d, ticks: %d' % (instrs, ticks))
    print('output=%s' % list(map(chr, output_buffer)))


def main(code_file, data_file, input_file):
    with open(code_file, encoding="utf-8") as file:
        instructions = json.loads(file.read())
    with open(data_file, encoding="utf-8") as file:
        data = json.loads(file.read())
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_buffer = []
        for char in input_text:
            input_buffer.append(char)
    simulate(instructions, data, input_buffer)

if __name__ == "__main__":
    assert len(sys.argv) == 4, "Wrong arguments: machine.py <code_file> <data_file> <input_file>"
    _, code_file, data_file, input_file = sys.argv
    main(code_file, data_file, input_file)