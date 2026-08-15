import time

TICK_DELAY = 0.05

while (1):
    x = 0
    while (x < 5):
        print("Looping...")
        x = x + 1
        time.sleep(TICK_DELAY)
    time.sleep(TICK_DELAY)
