var i
i = 0
var greating
greating = "What is your name?"
while (i < 18) {
    print(greating[i])
    i = i + 1
}
var username
username = "____________________________________________________________________________________________________"
var n
n = 0
i = 0
while (i < 100) {
    username[i] = input()
    if (username[i] == 10) {
        i = 100
    }
    if (username[i] != 0) {
        n = n + 1
    }
    i = i + 1
}
var s
s = "Hello, "
i = 0
while (i < 7) {
    print(s[i])
    i = i + 1
}
i = 0
while (i < n) {
    print(username[i])
    i = i + 1
}
print(33)
