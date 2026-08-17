import time

TICK_DELAY = 0.05

while True:
    userinput = input("Enter a number to count to: ")
    i = 1
    while (i <= int(userinput)):
        print(i)
        i += 1
        time.sleep(TICK_DELAY)
    time.sleep(TICK_DELAY)
