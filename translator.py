"""
var x
var c
var a
var s
print('h')
print(c)
x = 2
c = 'x'
c = input()
d = [11, 22, 33]
e = ['a', 'b', 'c']
print(e[0])
x = (2 + 2) - 3 * 4 / 4
e[0] = 3
var i
i = 2
e[i + 1] = 4
if (x < 10 and x >= 0 or x == 5 and x != 6) {
    x = x + 1
    y = x + 1
} else {
}
var i 
i = 0
while (i < 0) {
    i = i + 1
}
"""

"""
letter ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" 

digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

variable_name ::= letter (letter | digit)*

number ::= ( digit ) +

char ::= "'" <any symbol> "'"

string ::= "\"" <any symbol except a double quote>  "\""

array_access ::= variable_name "[" expression "]"        

operator ::= "+" | "-" | "*" | "/" | "%" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "and" | "or"

expression ::= 
    number |
    char |
    string |
    array |
    variable_name |
    array_access |
    expression operator expression |
    "(" expression ")" |
    "input" "(" ")" |
    "print" "(" experession ")"
    
statement ::= 
    "var" variable_name |
    "if" "(" expression ")" "{" ( statement ) * "}" 
    ( "else" "{" ( statement ) * "}" ) ? |
    "while" "(" expression ")" "{" ( statement ) * "}" |
    variable_name "=" expression |
    array_access "=" expression

program ::= ( statement ) +
"""
# x = (1 + 2) - 3 * 4 / 5
# 
# 1 2 +  3 4 * 5 /   -
# 
# ld 1            ; a == 1
# {
#     "op_code": "LD",
#     "operand_type": "number",
#     "operand_type": "memory",
#     "operand": 2,
# },
# add 2           ; a == 1 + 2
# st [1000]       ; [1000] == 3
# ld 3            ; a == 3
# mul 4           ; a == 3 * 4
# div 5           ; a == 3 * 4 / 5
# st [1001]       ; [1001] == 2
# ld [1000]       ; a == 3
# sub [1001]      ; 3 - 2
# out
# 
# [ a b c d ] registers
# 
# lda 1001
# add a, 1
# 
# Набор инстркции
# Вычисления
# 
# ADD operand      +
# SUB operand      +
# MUL operand      *
# DIV operand      /
# MOD operand      %
# AND operand      ?
# OR operand       ?
# SHL operand      ?
# SHR operand      ?
# Доступ к памяти
# 
# LD opreand      +
# ST address      +
# Работа со стеком
# 
# PUSH            ?
# POP (The popped element is discarded and not stored in ACC)  ?
# 
# 
# Branching
# 
# CMP operand         +
# JZ address          +
# JNZ address         +
# JB address          +
# JBE address         +
# JA address          +
# JAE address         +
# JMP address         +
# 
# 
# Управление Control Unit
# 
# HLT - Устанавливает флаг HLT в Control Unit   +


# ['var', 'a', 'var', 'b', 'var', 'c', 'print', '(', 'a', ')', 'if', '(', 'c', '>', '5', '{', 'print', '(', 'b', ')', '}']

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

#not worked
p1 = """
1 - 2 + 3 * (4 - 5) + 6
"""
#work
p = """
1 + 2 - 3 
"""
#not worked
p2 = """
x + y - x
"""
#work
p3 = """
1 + 2 - 3 var a
""" 
p4 = """
1 + 2 + 3 * 4
""" 

# print(tokenize(p3))

# ['x', 'y', 'z']
# 'y'
# 1 * 4  ->  4

def syntax_error():
    print("Syntax error: Invalid syntax.")
    exit(1)

# syntax_error()

#todo: fix
def is_name(s):
    if str == '':
        return False
    if not isinstance(s, str) or not s.isidentifier() or not s.islower():
        return False
    keywords = {'var', 'if', 'else', 'while', 'input', 'print'}
    return s not in keywords    
    
# print(is_name('π'))  # false
# print( is_name('x') )  # true
# print( is_name('x2') )  # true
# print( is_name('abc') )  # true
# print( is_name('var') )  # false
# print( is_name('15') )  # false
# print( is_name('ABC') )  # false 
# print( is_name('') )  # false
# print( is_name(None) )  # false

def is_op(s):
    if not isinstance(s, str):
        return False
    operators = {'<', '<=', '==', '>=', '>', '!=', '+', '-', '*', '/', '%'}
    return s in operators

# print(is_op('<'))     # True
# print(is_op('<='))    # True
# print(is_op('=='))    # True
# print(is_op('>='))    # True
# print(is_op('>'))     # True
# print(is_op('!='))    # True
# print(is_op('+'))     # True
# print(is_op('-'))     # True
# print(is_op('*'))     # True
# print(is_op('/'))     # True
# print(is_op('%'))     # True
# print(is_op('x'))     # False
# print(is_op('123'))   # False
# print(is_op('var'))   # False
# print(is_op(None))    # False
# print(is_op(""))

def skip(tokens, position, expected_token):
    if position >= len(tokens):
        syntax_error()
    if tokens[position] != expected_token:
        syntax_error()
    return position + 1

# print( skip(['(', ')'], 0, '(') )   # 1
# print( skip(['(', ')'], 1, ')') )   # 2
# 
# print( skip(['(', ')'], 0, 'a') )   # syntax_error
# print( skip(['(', ')'], 1, 'b') )   # syntax_error

def is_higher_op(new_op, base_op):
    priority = {'*': 2, '/': 2, '%': 2, '+': 1, '-': 1, '<': 0, '<=': 0, '==': 0, '!=': 0, '>=': 0, '>': 0}
    return priority.get(new_op, -1) > priority.get(base_op, -1)

# print( is_higher_op('*', '+') )   # true
# print( is_higher_op('/', '+') )   # true
# print( is_higher_op('%', '+') )   # true
# 
# print( is_higher_op('+', '==') )   # true
# print( is_higher_op('+', '-') )   # false
# 
# print( is_higher_op('+', '<') )   # true
# print( is_higher_op('+', '<=') )   # true
# print( is_higher_op('+', '==') )   # true
# print( is_higher_op('+', '!=') )   # true
# print( is_higher_op('+', '>=') )   # true
# print( is_higher_op('+', '>') )   # true
# 
# print( is_higher_op('xyz', '>') )   # false
# print( is_higher_op(None, '>') )   # false

def get_token(tokens, pos):
    if pos < len(tokens):
        return tokens[pos]
    else:
        return ''

# print( get_token(['a', 'b', 'c'], 0) )  # 'a'
# print( get_token(['a', 'b', 'c'], 1) )  # 'b'
# print( get_token(['a', 'b', 'c'], 2) )  # 'c'
# print( get_token(['a', 'b', 'c'], 3) )  # ''

def is_compare_op(op):
    operators = {'>', '<', '>=', '<=', '==', '!='}
    return op in operators

def arith_opcode(op):
    if is_compare_op(op):
        return "cmp"
    else:
        opcodes = {
            '+': 'add', 
            '-': 'sub', 
            '*': 'mul', 
            '/': 'div', 
            '%': 'mod'
        }
        return opcodes.get(op, '')

# print( arith_opcode("+") )   # "add"
# print( arith_opcode("-") )   # "sub"
# print( arith_opcode("*") )   # "mul"
# print( arith_opcode("/") )   # "div"
# print( arith_opcode("%") )   # "mod"

def cmp_jump_opcode(operator):
    opcodes = {'<': 'jb', '<=': 'jbe', '==': 'je', '>=': 'jae', '>': 'ja', '!=': 'jne'}
    return opcodes.get(operator, '')

# print( cmp_jump_opcode('<') )   # jb
# print( cmp_jump_opcode('<=') )  # jbe
# print( cmp_jump_opcode('==') )  # je
# print( cmp_jump_opcode('>=') )  # jae
# print( cmp_jump_opcode('>') )   # ja
# print( cmp_jump_opcode('!=') )  # jne


def alloc_temp_var(program):
    next_address = program["data_size"]
    temp_var_name = str(next_address)
    program["variables"][temp_var_name] = next_address
    program["data_size"] += 4  
    return next_address

# variable is 4 bytes
# unless otherwise specified (parameter size)
def alloc_var(program, name, size=4):
    next_address = program["data_size"]
    program["variables"][name] = next_address
    program["data_size"] += size
    return next_address

def save_acc(program):
    temp_var_address = alloc_temp_var(program)
    program["instructions"].append({"opcode": "st", "arg_type": "address", "arg": temp_var_address})
    return temp_var_address

def emit(progam, opcode, arg_type="none", arg=None):
    if opcode == "hlt":
        program["instructions"].append({
            "opcode": opcode, 
            "arg_type": arg_type
        })     
    else:
        program["instructions"].append({
            "opcode": opcode, 
            "arg_type": arg_type, 
            "arg": arg
        })

def emit_op(progam, op, arg_type="none", arg=None):
    opcode = arith_opcode(op)
    emit(program, opcode, arg_type, arg)
    if is_compare_op(op):
        cmp_addr = len(program['instructions']) - 1
        jump_opcode = cmp_jump_opcode(op)
        emit(program, jump_opcode, "address", cmp_addr + 4)
        emit(program, "ld", "immediate", 0)
        emit(program, "jmp", "address", cmp_addr + 5)
        emit(program, "ld", "immediate", 1)

# emits instruction to join two calculations
def join_expressions(program, left_addr, op):
    # place value of [left_addr] into accumulator
    # and place the current of accumulator into 
    # a temporary variable
    right_addr = save_acc(program)
    program["instructions"].append({"opcode": "ld", "arg_type": "address", "arg": left_addr})        
    # emit instruction for operation (f.ex. SUB [RIGHT_ADDR])
    emit_op(program, op, "address", right_addr)    
    # program["instructions"].append({"opcode": opcode, "arg_type": "address", "arg": right_addr})

def string_to_bytes(s):
    return [ord(char) for char in s]

# print(string_to_bytes('abc'))

# 123 x x2
def is_simple_operand(token):
    return token.isdigit() or is_name(token)
    
def address_of(program, name):
    if name in program["variables"]:
        return name
    else:
        syntax_error()
    
#todo:
#todo: strings
def parse_expression(tokens, pos, program):
    variables = program["variables"]

    token = get_token(tokens, pos)
    if token == '':
        syntax_error()
    # next_token = get_token(tokens, pos + 1)

    #todo: support `(`
    if is_simple_operand(token):
        if token.isdigit():
            emit(program, "ld", "immediate", int(token))
        elif is_name(token):
            emit(program, "ld", "address", address_of(program, token))
    # else:  (todo)
            
    pos += 1
    
    while is_op(op := get_token(tokens, pos)):
        next_op = get_token(tokens, pos + 2)
        if is_higher_op(next_op, op):
            left_addr = save_acc(program)
            pos = parse_expression(tokens, pos + 1, program)
            join_expressions(program, left_addr, op)
        else:  # the same precedence
            arg = get_token(tokens, pos + 1)           
            if is_simple_operand(arg):
                if arg.isdigit():
                    emit_op(program, op, "immediate", int(arg))
                elif is_name(token):
                    emit_op(program, op, "address", address_of(program, arg))
            pos += 2

    return pos


program = {
    "instructions": [],
    "variables": {
        "a": 0
    },
    "data_size": 4
}
parse_expression(tokenize("""
    2 * 2 == 1 - 4
"""), 0, program)
i = 0
for x in program['instructions']:
    print(i, x)
    i += 1

# lhs_addr = alloc_temp_var(program)
# program["instructions"].append({"opcode": "ld", "arg_type": "address", "arg": lhs_addr})
# print(join_expressions(program, lhs_addr, "+"))

# print( alloc_var(program, 'b') )   # 4
# print( alloc_var(program, 'c') )   # 8
# 
# print(program["variables"])  # {a: 0, b: 4, c: 8}
# print(program["data_size"])  # 12

# print(alloc_temp_var(program))   # 4
# print(alloc_temp_var(program))   # 8
# 
# print(program["variables"])  # {'a': 0, '4': 4, '8': 8}
# print(program["data_size"])  # 12

# print( save_acc(program) )   # 4
#parse_expression(tokenize("x + y"), 0, program)
# print(program)

#result func parse_expression if use test 'p'
[
    {
        "opcode": "ld",
        "arg_type": "immediate",
        "arg": 1
    },
    {
        "opcode": "add",
        "arg_type": "immediate",
        "arg": 2    
    },
    {
        "opcode": "sub",
        "arg_type": "immediate",
        "arg": 3
    },
]

# var +
# `x =` -
# if - 
# while - 
# `print` -
# `input` - 
def parse_statement(tokens, pos, program):
    instructions = program["instructions"]
    variables = program["variables"]
    token = get_token(tokens, pos)
    if token == 'var':
        var_name = get_token(tokens, pos + 1)
        if is_name(var_name):
            alloc_var(program, var_name)
            return pos + 2
        else:
            raise ValueError("Invalid variable name")

# done            
def parse_program(tokens):
    program = {
        "instructions": [],
        "variables": {},
        "data_size": 0
    }
    pos = 0
    while pos < len(tokens):
        pos = parse_statement(tokens, pos, program)
    return program

# Пример использования:
program_code = """
    var a
    var b
"""

program = parse_program(tokenize(program_code))

# print(tokenize(program_code))
# print(program["variables"])  # {'a': 0, 'b': 4} - две новые переменные введены


# parse_statement("var b", 0, program)
# 
# print(program["variables"])  # {'a': 0, 'b': 4}
# 
# def parse_program(tokens):
#     instructors = []
#     pos = 0
#     while pos < len(tokens):
#         pos = parse_statement(tokens, pos, instructors)
#     return instructors
# 
# print(parse_program(tokenize(p)))

#todo: rewirte to our simplified js 
def sum_even_fibonacci(limit):
    sum_even = 0
    prev = 1
    current = 2
    
    while current <= limit:
        if current % 2 == 0:
            sum_even += current
            
        prev, current = current, prev + current
    
    # print(
    return sum_even

def cat():
    stop_char = '^D'
    char = input()
    while (char != stop_char):
        print(char)

# print(sum_even_fibonacci(4_000_000_000)) # числа 2 и 8 (1, 2, 3, 5, 8)
    
# should be:
# ['var', 'a', 'a', '=', '"hello world"', 'print', 
# '(', 'a', ')', 'if', '(', 'c', '>', '5', ')', 
# '{', 'print', '(', 'b', ')', '}'
