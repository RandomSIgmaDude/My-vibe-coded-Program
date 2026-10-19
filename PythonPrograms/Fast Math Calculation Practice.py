import random
import time
import os
import msvcrt

# ── Colors ───────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
ORANGE = "\033[38;5;208m"
RESET  = "\033[0m"


operators = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y if y != 0 else "Error: Division by zero",
    "**": lambda x, y: x ** y,
    "%": lambda x, y: x % y
}

# ── Utilities ────────────────────────────────────────────
def time_color(t):
    if t <= 1.5: return BLUE
    if t <= 2.0: return YELLOW
    if t <= 3.5: return ORANGE
    return RED

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_below():
    """Clear from line 4 downward (keeps lines 1, 2, 3)"""
    print("\033[4;1H\033[J", end="", flush=True)

def user_input(message, choices):
    """Get integer input. If choices is None, accept any int."""
    while True:
        try:
            user = int(input(message))
            if not choices:
                return user
            if user in choices:
                return user
            else:
                print(f"  Invalid choice. Choices: {choices}")
        except Exception as e:
            print(f"  {e} Please try again.")

def smart_input(answer):
    """Auto-submits once enough digits are typed (based on |answer|, i.e. n > 0).
    A leading '-' can be typed first; it doesn't count toward the digit total,
    so negative subtraction answers auto-submit too instead of needing Enter.
    Enter still works as a manual fallback."""
    digits_needed = len(str(abs(answer)))
    typed = ""

    def digit_count(s):
        return len(s) - (1 if s.startswith("-") else 0)

    while True:
        ch = msvcrt.getwch()

        if ch == '\x08':                            # Backspace
            if typed:
                typed = typed[:-1]
                print("\b \b", end="", flush=True)

        elif ch == '\r':                            # Enter (manual submit / fallback)
            if typed and typed != "-":
                print()
                try:
                    return int(typed)
                except ValueError:
                    typed = ""
                    print(f"\r  → {' ' * digits_needed}\r  → ", end="", flush=True)

        elif ch == '-' and typed == "":             # Minus (first char only)
            typed += ch
            print(ch, end="", flush=True)

        elif ch.isdigit():                          # Digit
            typed += ch
            print(ch, end="", flush=True)
            if digit_count(typed) == digits_needed:
                print()
                return int(typed)

        else:                                       # Invalid — reset
            typed = ""
            print(f"\r  → {' ' * digits_needed}\r  → ", end="", flush=True)

def get_range_input(i):
    """Ask for a random range in 'min max' format. Type 1 for help."""
    while True:
        raw = input(f'  Range {i} → enter [1] for help: ').strip()

        if raw == "1":
            print('    Format   : "min max"')
            print('    Examples : "1 99"  |  "10 50"  |  "100 999"')
            print('    Rule     : first number must be less than the second\n')
            continue

        parts = raw.split()
        if len(parts) != 2:
            print('    Invalid. Use: "min max"  (e.g. "1 99")\n')
            continue

        try:
            lo, hi = int(parts[0]), int(parts[1])
            if lo > hi:
                print('    First number must be less than the second.\n')
                continue
            return lo, hi
        except ValueError:
            print('    Invalid. Both must be whole numbers  (e.g. "12 345")\n')


#  Base class — shared game state + behavior
class GameMode:
    name = "Game Mode"

    def __init__(self):
        self.score       = 0
        self.total_score = 0
        self.times       = []

    @property
    def avg_time(self):
        return round(sum(self.times) / len(self.times), 2) if self.times else 0.00

    def reset(self):
        print(f"\n  Resetting...  Last score: {self.score}/{self.total_score}  |  Avg: {self.avg_time}s")
        input("  Press Enter to continue...")
        self.score       = 0
        self.total_score = 0
        self.times       = []

    def exit(self):
        print(f"\n  Exiting...  Score: {self.score}/{self.total_score}  |  Avg: {self.avg_time}s")

    def handle_commands(self, answer):
        """Returns True if answer was a command (-1 exit, -2 reset)."""
        if answer == -123456:
            self.exit()
            return "exit"
        if answer == -1234567:
            self.reset()
            return "reset"
        return None

    def track(self, elapsed, answer, correct):
        """Score + time tracking for a normal answer."""
        self.total_score += 1
        self.times.append(elapsed)
        tc = time_color(elapsed)

        if answer == correct:
            self.score += 1
            print(f"  {GREEN}Correct!{RESET}  Took {tc}{elapsed}s{RESET}")
        else:
            print(f"  {RED}Wrong! Answer was {correct}{RESET}  |  Took {tc}{elapsed}s{RESET}")

    def setup(self):
        """Override in subclass for pre-game setup."""
        pass

    def run(self):
        """Override in subclass for game loop."""
        raise NotImplementedError


# ════════════════════════════════════════════════════════
#  Mode 1 — All At Once
# ════════════════════════════════════════════════════════
class AllAtOnce(GameMode):
    name = "All at Once"

    def __init__(self):
        super().__init__()
        self.numbers_to_random = {}
        self.operator = ""

    def setup(self):
        while True:
            operation = input("  operator [+,-,*,/] -> ")
            if operation not in ["+", "-", "*", "/"]:
                print("Invaild please try again")
                continue
            else:
                self.operator = operation
            
            break

        count = user_input("  How many numbers to add up → ", None)
        for i in range(1, count + 1):
            lo, hi = get_range_input(i)
            self.numbers_to_random[i] = (lo, hi)

    def run(self):
        clear_screen()
        print("⚡  Fast Math Calculation!  (Addition)")         # line 1 — never cleared
        print(f"    {YELLOW}[-123456]{RESET} Exit    {YELLOW}[-1234567]{RESET} Reset\n")  # line 2

        self.setup()

        while True:
            nums     = [random.randint(v[0], v[1]) for v in self.numbers_to_random.values()]
            correct  = nums[0]
            for i in range(1, len(nums)):
                num = nums[i]
                correct = operators[self.operator](correct, num)

            equation = f" {self.operator} ".join(map(str, nums))
            atc      = time_color(self.avg_time)

            clear_below()
            print(f"  [{self.score}/{self.total_score}]  avg: {atc}{self.avg_time}s{RESET}")
            print(f"  {equation}  =  ?")
            print("  → ", end="", flush=True)

            start   = time.time()
            answer  = smart_input(correct)
            elapsed = round(time.time() - start, 2)

            cmd = self.handle_commands(answer)
            if cmd == "exit":  return
            if cmd == "reset": continue

            self.track(elapsed, answer, correct)
            time.sleep(0.5)


class FastThinking(GameMode):
    name = "All at Once"

    def __init__(self):
        super().__init__()
        self.numbers_to_random = {}
        self.apearing_time = 1
        self.operator = ""

    def setup(self):
        pass


# ════════════════════════════════════════════════════════
#  Menu — creates instances and runs them
# ════════════════════════════════════════════════════════
MODES = {
    1: AllAtOnce,
    2: FastThinking,        # FastThinking  (coming soon)
    3: None,        # More          (coming soon)
}

def menu():
    while True:
        clear_screen()
        print("⚡  Fast Math Calculation!")
        print("  [0]  Exit")
        print("  [1]  All at once  (1 + 23 + 12 + ... = ?)")
        print("  [2]  Fast thinking  (number appears only once)")
        print("  [3]  More")

        choice = user_input("  → ", [0, 1, 2, 3])

        if choice == 0:
            return

        mode_class = MODES.get(choice)

        if mode_class:
            game = mode_class()   # create instance
            game.run()            # do whatever
        else:
            print("\n  Coming soon...")
            input("  Press Enter to continue...")

menu()
