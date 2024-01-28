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
len(d)
print(e[0])
x = (2 + 2) - 3 * 4 / 4
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

p = """
1 - 2 + 3 * (4 - 5) + 6
"""
print(tokenize(p))
# should be:
# ['var', 'a', 'a', '=', '"hello world"', 'print', 
# '(', 'a', ')', 'if', '(', 'c', '>', '5', ')', 
# '{', 'print', '(', 'b', ')', '}'
