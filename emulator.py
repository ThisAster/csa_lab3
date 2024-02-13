def int32(x):
    full_range = 2 ** 8
    half_range = 2 ** 8 // 2
    unsigned = x + half_range           # go to unsinged
    wrapped = unsigned % full_range     # overflow/underflow
    signed = wrapped - half_range       # go back
    return signed

# print(int32(100))

class Multiplexer:
    input0: int = 0
    input1: int = 0
    input2: int = 0
    input3: int = 0
    sel: int = 0
    output: int = 0
    def simulate(self):
        if self.sel == 0:
            self.output = self.input0
        elif self.sel == 1:
            self.output = self.input1
        elif self.sel == 2:
            self.output = self.input2
        elif self.sel == 3:
            self.output = self.input3
            
class Register:
    input0: int = 0
    _latch: int = 0
    latch: int = 0
    _value: int = 0
    output: int = 0
    def simulate(self):
        if self._latch == 0 and self.latch == 1:
            self._value = self.input0
            self._latch = 1
        else:
            self._latch = self.latch
        self.output = self._value
    
class ALU:
    input0: int = 0
    input1: int = 0
    sel: int = 0
    output: int = 0
    def simulate(self):
        if self.sel == 0:
            self.output = self.input0 + self.input1
        elif self.sel == 1:
            self.output = self.input0 - self.input1            
        #todo: all other operations

class IsZeroOp:
    input0: int = 0
    output: int = 0
    def simulate(self):
        if self.input0 == 0:
            self.output = 1
        else:
            self.output = 0
    
class IsNegativeOp:    
    input0: int = 0
    output: int = 0
    def simulate(self):
        if self.input0 < 0:
            self.output = 1
        else:
            self.output = 0
            
class Memory:
    input0: int = 0
    address: int = 0
    _write: int = 0
    write: int = 0
    _read: int = 0
    read: int = 0
    output: any = 0
    _data: list
    def __init__(self, data):
        self._data = data
    def simulate(self):
        if self._read == 0 and self.read == 1:
            self.output = self._data[self.address]
        self._read = self.read            
        if self._write == 0 and self.write == 1:
            self._data[self.address] = self.input0
        self._write = self.write

class InputPort:
    input_buffer: list
    _read: int = 0
    read: int = 0
    output: int = 0
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
    def simulate(self):
        if self._read == 0 and self.read == 1:
            self.output = input_buffer.pop(0)
        self._read = self.read                    
        
class OutputPort:
    input0: int = 0
    output_buffer: list
    _write: int = 0
    write: int = 0
    def __init__(self, output_buffer):
        self.output_buffer = output_buffer
    def simulate(self):
        if self._write == 0 and self.write == 1:
            self.ouput_buffer.append(self.input0)
        self._write = self.write                    
        
class DataPath:
    # external signals from ControlUnit
    instruction_arg: int = 0   
    latch_data_address: int = 0
    data_address_sel: int = 0
    input_port_read: int = 0
    acc_sel: int = 0
    latch_acc: int = 0
    output_port_write: int = 0
    alu_operand_sel: int = 0
    alu_operation_sel: int = 0
    data_read: int = 0
    data_write: int = 0
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
    # output signals
    zero_flag: int
    negative_flag: int
    # input/output
    # input_buffer: list
    # output_buffer: list
    def __init__(self, data_memory, input_buffer, output_buffer):    
        self.data_address_mux = Multiplexer()
        self.data_address = Register()
        self.data_memory = Memory(data_memory)
        self.acc_mux = Multiplexer()
        self.input_port = InputPort(input_buffer)
        self.acc = Register()
        self.output_port = OutputPort(output_port)
        self.alu_mux = Multiplexer()
        self.alu = ALU()
        self.is_zero_op = IsZeroOp()
        self.is_negative_op = IsNegativeOp()
        # # input/output
        # self.input_buffer = input_buffer
        # self.output_buffer = output_buffer
    def simulate(self):
        # internal components
        self.data_address_mux.input0 = self.instruction_arg
        self.data_address_mux.input1 = self.data_memory.output
        self.data_address_mux.sel = self.data_address_sel
        self.data_address_mux.simulate()
        
        self.data_address.input0 = self.data_address_mux.output
        self.data_address.latch = self.latch_data_address
        self.data_address.simulate()
        
        self.data_memory.input0 = self.acc.output   
        self.data_memory.read = self.data_read
        self.data_memory.write = self.data_write
        self.data_memory.address = self.data_address.output
        self.data_memory.simulate()
        
        self.input_port.read = input_port_read
        
        self.acc_mux.input0 = self.instruction_arg
        self.acc_mux.input1 = self.input_port.output
        self.acc_mux.input2 = self.data_memory.output
        self.acc_mux.input3 = self.alu.output
        self.acc_mux.sel = self.acc_sel
        self.acc_mux.simulate()
        
        self.acc.input0 = self.acc_mux.output
        self.acc.latch = self.latch_acc
        self.acc.simulate()
        
        self.output_port.input0 = self.acc.output
        self.output_port.write = output_port_write
        
        self.alu_mux.input0 = self.data_memory.output
        self.alu_mux.input1 = self.instruction_arg
        self.alu_mux.sel = self.alu_operand_sel
        self.alu_mux.simulate()
        
        self.alu.input0 = self.acc.output
        self.alu.input1 = self.alu_mux.output
        self.alu.sel = self.alu_operation_sel
        self.alu.simulate()
        
        self.is_zero_op.input0 = self.alu.output
        self.is_zero_op.simulate()
        
        self.is_negative_op.input0 = self.alu.output
        self.is_negative_op.simulate()
        
        # output signals
        self.zero_flag = self.is_zero_op.output
        self.negative_flag = self.is_negative_op.output

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
    input0: int = 0
    output: int = 0
    def simulate(self):
        self.output = input0 + 1

class AndOp:     
    input0: int = 0
    input1: int = 0
    output: int = 0
    def simulate(self):
        if self.input0 == 1 and self.input1 == 1:
            self.output = 1
        else:
            self.output = 0
    
class OrOp:
    input0: int = 0
    input1: int = 0
    output: int = 0
    def simulate(self):
        if self.input0 == 0 and self.input1 == 0:
            self.output = 0
        else:
            self.output = 1
        
class ControlUnit:
    data_path: DataPath
    program_counter_mux: Multiplexer
    program_counter: Register
    increment_pc: IncrementOp
    code_memory: Memory
    micro_program_counter_mux: Multiplexer
    micro_program_counter: Register
    increment_mpc: IncrementOp
    microcode_memory: Memory
    zero_jump_and: AndOp
    negative_jump_and: AndOp
    jump_or: OrOp
    input_buffer: list
    output_buffer: list
    def __init__(self, data_path, code_memory, microcode_memory, input_buffer, output_buffer):
        self.data_path = data_path
        self.program_counter_mux = Multiplexer()
        self.program_counter = Register()
        self.increment_pc = IncrementOp()
        self.code_memory = code_memory
        self.micro_program_counter_mux = Multiplexer()
        self.micro_program_counter = Register()
        self.increment_mpc = IncrementOp()
        self.microcode_memory = microcode_memory
        self.negative_jump_and = AndOp()
        self.negative_jump_and = AndOp()
        self.jump_or = OrOp()
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer
    def simulate(self):
        # instructruction_arg = 
        # latch_code_address = 
        # code_memory_read
        
        self.program_counter_mux.input0 = instructraction_arg
        self.program_counter_mux.input1 = self.increment_pc.output
        self.program_counter_mux.sel = self.jump_or.ouput
        
        self.program_counter.input0 = self.program_counter_mux.output
        self.program_counter.latch = latch_code_address
        
        self.increment_pc.input0 = self.program_counter.output
        
        self.code_memory.address = self.program_counter.output
        self.code_memory.read = code_memory_read
        
        # self.code_memory.output
        
        # instruction opcode + arg_type
        # ----> micro-instruction address
        # opcode_address = ...
        
        self.micro_program_counter_mux.input0 = opcode_address
        self.micro_program_counter_mux.input1 = ...
        self.micro_program_counter_mux.sel = ...
        
        self.micro_code_memory.output
        
        # self.micro_code_memory.output
        # ---------> signals below:
        
        # self.data_path.instruction_arg: int = 0   
        # self.data_path.latch_data_address: int = 0
        # self.data_path.data_address_sel: int = 0
        # self.data_path.input_port_read: int = 0
        # self.data_path.acc_sel: int = 0
        # self.data_path.latch_acc: int = 0
        # self.data_path.output_port_write: int = 0
        # self.data_path.alu_operand_sel: int = 0
        # self.data_path.alu_operation_sel: int = 0
        # self.data_path.data_read: int = 0
        # self.data_path.data_write: int = 0        
    
# def execute():

        
"""        
class ControlUnit:
    data_path = None
    code_memory = None
    progam_counter = None
    input_buffer = None
    output_buffer = None
    microcode_memory = None
    def __init__(self, data_path, code_memory, input_buffer):
        self.data_path = data_path
        self.code_memory = code_memory
        self.program_counter = 0
        self.input_buffer = input_buffer    
        self.output_buffer = []
        microcode_memory = [
            # acc_sel 2,
            # latch_acc,
            # end,
        ]
    def simulate(self):
        while opcode != 'hlt' or input_buffer != []:
            instruction = self.code_memory[i]
            opcode = instruction['opcode']
            arg_type = instruction['arg_type']
            arg = instruction.get('arg', None)
            if opcode == 'ld':
                if arg_type == 'immediate':
                    self.data_path.acc = arg
                else:
                    self.data_path.acc = self.data_path.data_memory[arg]
            elif opcode == 'st':
                self.data_path.data_memory[arg] = self.data_path.acc
            elif opcode == 'out':
                self.output_buffer.append(self.data_path.acc)
            elif opcode == 'in':
                self.data_path.acc = ord(self.input_buffer.pop(0))
            elif opcode =='add':
                if arg_type == 'immediate':
                    self.data_path.acc += arg
                else:
                    self.data_path.acc += self.data_path.data_memory[arg]
            elif opcode == 'sub':
                if arg_type == 'immediate':
                    self.data_path.acc -= arg
                else:
                    self.data_path.acc -= self.data_path.data_memory[arg]
            elif opcode == 'hlt':
                break        

def execute(code_memory, data_memory, input_buffer):
    data_path = DataPath(data_memory)
    control_unit = ControlUnit(data_path, code_memory, input_buffer)
    control_unit.simulate()    
    return control_unit.output_buffer

output = execute(
    program['instructions'], 
    program['data'], 
    ['A', 'l', 'i', 'c', 'e']
)
print(output)
print(program['data'])
"""
