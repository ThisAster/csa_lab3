import sys
import json

def tokenize(s):
    separators = {'(', ')', '{', '}', '[', ']', ' ', '\n'}
    result = []
    current_word = ''
    inside_quotes = False
    
    for char in s:
        if char == '"':
            if inside_quotes:
                inside_quotes = False
            else:
                inside_quotes = True
        
        if char in separators and not inside_quotes:
            if current_word:
                result.append(current_word)
                current_word = ''
            if char != ' ' and char != '\n':
                result.append(char)
        else:
            current_word += char

    if current_word:
        result.append(current_word)
    
    return result

def syntax_error(reason='Invalid syntax.'):
    print('Syntax error: %s' % reason)
    # assert False
    exit(1)
    
def get_token(tokens, pos):
    if pos < len(tokens):
        return tokens[pos]
    else:
        return ''
    
def skip(tokens, position, expected_token):
    if position >= len(tokens):
        syntax_error('Parsing past end of file.')
    token = tokens[position]
    if token != expected_token:
        syntax_error('`%s` expected, but `%s` found' % (expected_token, token))
    return position + 1        
    
def is_name(s: str):
    if s != '' and s.isalpha() and s.islower():
        keywords = {'var', 'if', 'while', 'input', 'print'}
        return s not in keywords
    else:
        return False

def is_op(s):
    operators = {
        '<', '<=', '==', '>=', '>', '!=', 
        '+', '-', '*', '/', '%', '['
    }
    return s in operators

def is_compare_op(op):
    operators = {'<', '<=', '==', '>=', '>', '!='}
    return op in operators    

def is_higher_op(new_op, base_op):
    priority = {'*': 2, '/': 2, '%': 2, '+': 1, '-': 1, '<': 0, '<=': 0, '==': 0, '!=': 0, '>=': 0, '>': 0}
    return priority.get(new_op, -1) > priority.get(base_op, -1)

def arith_opcode(op):
    if is_compare_op(op):
        return "sub"  # used instead of `cmp`
    else:
        opcodes = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod'}
        return opcodes.get(op, '')

def cmp_jump_opcode(operator):
    opcodes = {'<': 'jl', '<=': 'jle', '==': 'je', '>=': 'jge', '>': 'jg', '!=': 'jne'}
    return opcodes.get(operator, '')

def emit(program, opcode, arg_type="none", arg=0):
    program["instructions"].append({
        "opcode": opcode, 
        "arg_type": arg_type, 
        "arg": arg
    })
    # return address of the last emitted instruction
    return len(program["instructions"]) - 1

def emit_op(program, op, arg_type, arg):
    opcode = arith_opcode(op)
    instruction_addr = emit(program, opcode, arg_type, arg)
    if is_compare_op(op):
        # set accumulator to 1 or 0 according to flags
        jump_opcode = cmp_jump_opcode(op)
        emit(program, jump_opcode, "address", instruction_addr + 4)
        emit(program, "ld", "immediate", 0)
        emit(program, "jmp", "address", instruction_addr + 5)
        emit(program, "ld", "immediate", 1)
    return instruction_addr

def alloc_var(program, name):
    next_address = program["data_size"]
    program["variables"][name] = next_address
    program["data_size"] += 1  
    return next_address

def alloc_temp_var(program):
    next_address = program["data_size"]
    temp_var_name = str(next_address)
    return alloc_var(program, temp_var_name)

def string_to_bytes(s):
    chars = [ord(char) for char in s]
    chars.append(0)  # zero-terminator for c-string
    return chars

def alloc_string(tokens, pos, program):
    token = get_token(tokens, pos)
    text = token[1:-1]  # drop quotes
    char_codes = string_to_bytes(text)
    data_addr = program['data_size']
    for i in range(len(char_codes)):
        program['data'][data_addr + i] = char_codes[i] 
    program['data_size'] += len(char_codes) 
    return data_addr

def address_of(program, name):
    if name in program["variables"]:
        return program["variables"][name]
    else:
        syntax_error('Unknown variable')

def save_acc(program):
    temp_var_address = alloc_temp_var(program)
    emit(program, "st", "address", temp_var_address)
    return temp_var_address

# emits instruction to join two calculations
def join_expressions(program, left_addr, op):
    # place value of [left_addr] into accumulator
    # and place the current value of accumulator into 
    # a temporary variable
    right_addr = save_acc(program)
    emit(program, "ld", "address", left_addr)        
    # emit instruction for operation (f.ex. SUB [RIGHT_ADDR])
    emit_op(program, op, "address", right_addr)    

def is_simple_operand(token):
    return token.isdigit() or is_name(token)
    
def parse_expression(tokens, pos, program, one_operand=False):
    token = get_token(tokens, pos)
    if token == '':
        syntax_error()

    if is_simple_operand(token):
        if token.isdigit():
            emit(program, "ld", "immediate", int(token))
        elif is_name(token):
            emit(program, "ld", "address", address_of(program, token))
        pos += 1
    elif token[0] == '"':
        data_addr = alloc_string(tokens, pos, program)
        emit(program, "ld", "immediate", data_addr)
        pos += 1
    elif token == '(':
        pos = skip(tokens, pos, '(')
        pos = parse_expression(tokens, pos, program)
        pos = skip(tokens, pos, ')')
        if one_operand:
            return pos
    elif token == "input":
        pos = skip(tokens, pos, 'input')
        pos = skip(tokens, pos, '(')
        emit(program, "in", "address", 0)
        pos = skip(tokens, pos, ')')
        if one_operand:
            return pos
    else:
        syntax_error()
    
    while is_op(op := get_token(tokens, pos)):
        token = get_token(tokens, pos + 1) 
        next_op = get_token(tokens, pos + 2)
        if token == '(':
            left_addr = save_acc(program)
            pos = parse_expression(tokens, pos + 1, program, True)
            join_expressions(program, left_addr, op)            
        elif op == '[':
            var_addr = save_acc(program)
            pos = skip(tokens, pos, '[')
            pos = parse_expression(tokens, pos, program)
            pos = skip(tokens, pos, ']')
            emit(program, "add", "address", var_addr)
            char_addr = save_acc(program)
            emit(program, "ld", "indirect_address", char_addr)                         
        elif token == "input":
            left_addr = save_acc(program)
            pos = parse_expression(tokens, pos + 1, program, True)            
            join_expressions(program, left_addr, op)            
        elif is_higher_op(next_op, op):
            left_addr = save_acc(program)
            pos = parse_expression(tokens, pos + 1, program)
            join_expressions(program, left_addr, op)
        else:  # operation with the same precedence
            if is_simple_operand(token):
                if token.isdigit():
                    emit_op(program, op, "immediate", int(token))
                elif is_name(token):
                    emit_op(program, op, "address", address_of(program, token))                  
            else:
                syntax_error()        
            pos += 2
    return pos

def parse_statement(tokens, pos, program):
    token = get_token(tokens, pos)
    if token == 'var':
        var_name = get_token(tokens, pos + 1)
        if is_name(var_name):
            alloc_var(program, var_name)
            return pos + 2
        else:
            syntax_error('Invalid variable name')
    elif token == "if":
        pos = skip(tokens, pos, 'if')
        pos = skip(tokens, pos, '(')
        pos = parse_expression(tokens, pos, program)
        # emit(program, "cmp", "immediate", 0)
        # emit(program, "sub", "immediate", 0)
        jmp_addr = emit(program, "je", "address", -1)
        pos = skip(tokens, pos, ')')
        pos = skip(tokens, pos, '{')
        while get_token(tokens, pos) != '}':
            pos = parse_statement(tokens, pos, program)
        pos = skip(tokens, pos, '}')
        if_end_addr = len(program["instructions"]) 
        program["instructions"][jmp_addr]['arg'] = if_end_addr
        return pos
    elif token == "while":
        pos = skip(tokens, pos, 'while')
        pos = skip(tokens, pos, '(')
        loop_start_addr = len(program["instructions"]) 
        pos = parse_expression(tokens, pos, program)
        # emit(program, "cmp", "immediate", 0)
        # emit(program, "sub", "immediate", 0)
        jmp_addr = emit(program, "je", "address", -1)
        pos = skip(tokens, pos, ')')
        pos = skip(tokens, pos, '{')
        while get_token(tokens, pos) != '}':
            pos = parse_statement(tokens, pos, program)
        pos = skip(tokens, pos, '}')
        emit(program, "jmp", "address", loop_start_addr)
        # fixup forward skip jump address        
        loop_end_addr = len(program["instructions"])
        program["instructions"][jmp_addr]['arg'] = loop_end_addr
        return pos
    elif token == "print":
        pos = skip(tokens, pos, 'print')
        pos = skip(tokens, pos, '(')
        pos = parse_expression(tokens, pos, program)
        pos = skip(tokens, pos, ')')
        emit(program, "out", "address", 0)
        return pos
    elif is_name(token) and get_token(tokens, pos + 1) == "=":  
        # simple assignment like x = 5, x = 2 * 3
        var_name = token
        var_addr = address_of(program, var_name)
        pos = parse_expression(tokens, pos + 2, program)
        emit(program, "st", "address", var_addr)
        return pos
    elif is_name(token) and get_token(tokens, pos + 1) == "[":
        # assignment to element of string, f.ex. s[i] = 97
        var_name = token
        var_addr = address_of(program, var_name)
        pos = parse_expression(tokens, pos + 2, program)
        emit(program, "add", "address", var_addr)  # [s] + A * 4       
        data_ptr = save_acc(program)
        pos = skip(tokens, pos, ']')
        pos = skip(tokens, pos, '=')
        pos = parse_expression(tokens, pos, program)
        # emit("st", "address", data_ptr)
        emit(program, "st", "indirect_address", data_ptr)
        return pos
    else:  
        syntax_error('Unrecognized statement: `%s`' % token)
        
def parse_program(tokens):
    program = {
        "instructions": [],
        "variables": {},
        "data": [0] * 1024,
        "data_size": 0
    }
    pos = 0
    while pos < len(tokens):
        pos = parse_statement(tokens, pos, program)
    emit(program, "hlt")
    return program

def filter_non_empty(lst):
    res = []
    for elem in lst:
        if elem.strip():     
            res.append(elem)
    return res

def translate(program_code):
    program = parse_program(tokenize(program_code))   
    lines = program_code.split('\n')
    loc = len(filter_non_empty(lines))
    num_instrs = len(program['instructions'])
    print('LoC: %s, code instructinos: %s' % (loc, num_instrs))
    return program

def write_code(filename, instructions):
    with open(filename, "w", encoding="utf-8") as file:
        buf = []
        for instr in instructions:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")   
        
def write_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        text = json.dumps(data)
        file.write(text)
    
def main(source, target_code, target_data):
    with open(source, encoding="utf-8") as f:
        source = f.read()
    program = translate(source)
    write_code(target_code, program['instructions'])
    write_data(target_data, program['data'])

if __name__ == "__main__":
    assert len(sys.argv) == 4, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target_code, target_data = sys.argv
    main(source, target_code, target_data)    