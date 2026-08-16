import time

TICK_DELAY = 0.05

while True:
    w_for = 1
    while (w_for <= 10):
        print(w_for)
        w_for = w_for + 1
        time.sleep(TICK_DELAY)
    time.sleep(TICK_DELAY)
