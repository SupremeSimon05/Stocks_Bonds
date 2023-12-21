import sys, select, threading, new, time

class main:
    cont=False
def move_cursor(x, y):
    print(f"\033[{y};{x}H", end="")

def process():
    while(True):
        while(main.cont):
            new.printing()

def check_input():
    time_passed = 0
    while time_passed < 3600 * 3:
        input_available, _, _ = select.select([sys.stdin], [], [], 1)
        if input_available:
            input()  # Read the input
            print("\033cTime skipped.", end=" ")
            return True
        else:
            time_passed += 1
            time_remaining = 3600 * 3 - time_passed
            move_cursor(0, new.get_terminal_size()[1])
            print(" ", time_remaining, "seconds remaining...", end="")
    if time_passed >= 3600 * 3:
        move_cursor(0, new.get_terminal_size()[1])
        print(22 * "  ", end="\r")
    move_cursor(0, new.get_terminal_size()[1])
    return False

def to_wait():
    # Create a thread for the process() function
    main.cont=True

    # Check for user input and stop the process if the input is received
    if check_input():
        # Terminate the process thread
        main.cont=False
    time.sleep(20)
process_thread = threading.Thread(target=process, daemon=True)
process_thread.start()