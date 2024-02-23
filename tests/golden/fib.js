var sumeven
sumeven = 0
var prev
prev = 1
var current
current = 2
var limit
limit = 4000000
var tempvar
while (current <= limit) {
    if (current % 2 == 0) {
        sumeven = sumeven + current
    }
    tempvar = prev
    prev = current
    current = tempvar + current
}

var digit
var sumreversed
sumreversed = 0
while (sumeven != 0) {
    digit = sumeven % 10
    sumreversed = sumreversed * 10 + digit
    sumeven = sumeven / 10
}

while (sumreversed != 0) {
    digit = sumreversed % 10
    print(48 + digit)
    sumreversed = sumreversed / 10
}
