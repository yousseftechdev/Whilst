import time

TICK_DELAY = 0.05

# Functions
def printRange(current, end):
    while current <= end:
        print("Value:", current)
        current = current + 1

while True:
    print("--- First Run (1 to 3) ---")
    printRange(1, 3)
    print("--- Second Run (10 to 12) ---")
    printRange(10, 12)
    time.sleep(TICK_DELAY)
