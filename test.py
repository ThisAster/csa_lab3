# Draft for tests
sum_even = 0
prev = 1
current = 2
limit = 4000000
while current <= limit:
    if current % 2 == 0:
        sum_even += current
    
    temp_var = prev
    prev = current
    current = temp_var + current

# Функция для вывода цифр числа по одной
def print_digits(number):
    if number == 0:
        print("0")
        return
    
    while number != 0:
        digit = number % 10
        print(digit)
        number //= 10

# Выводим цифры числа sum_even по одной
print_digits(sum_even)

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

print(sum_even_fibonacci(limit))