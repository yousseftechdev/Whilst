import time

TICK_DELAY = 0.05

# Functions
def alert(active, status):
    while active:
        print("ALERT:", status)
        active = 0

while True:
    temperature = 75
    is_hot = (temperature > 70)
    while (is_hot):
        flag = 1
        alert(flag, "Temperature threshold exceeded!")
        is_hot = 0
        time.sleep(TICK_DELAY)
    is_normal = (temperature <= 70)
    while (is_normal):
        print("Temperature within normal parameters.")
        is_normal = 0
        time.sleep(TICK_DELAY)
    print("Monitoring cycle complete.\n")
    time.sleep(1)
    time.sleep(TICK_DELAY)
