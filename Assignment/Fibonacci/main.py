from concurrency_model import ConcurrencyModel
from fibonacci_engine import FibonacciEngine


class ConcurrencyView:
    """
    View Layer: Handles CLI menu presentation and prints each round live
    in nanoseconds for both multithreaded and sequential runs.
    """
    @staticmethod
    def display_menu(targets, num_rounds):
        print("\n" + "=" * 72)
        print("      ==== Fibonacci Concurrent vs. Sequential Benchmark ====      ")
        print(f"      [Targets: Fib({targets[0]}), Fib({targets[1]}), Fib({targets[2]}) | Rounds: {num_rounds}]")
        print("=" * 72)
        print("  1. Run 10-Round Experiment (Iterative O(n) - Instant Execution)")
        print("  2. Run 10-Round Experiment (Recursive O(2^n) - Live Round Progress)")
        print("  3. Exit")
        print("-" * 72)

    @staticmethod
    def get_int_input(prompt, min_val=None, max_val=None):
        while True:
            raw = input(prompt).strip()
            try:
                val = int(raw)
                if min_val is not None and val < min_val:
                    print(f"  [!] Value must be at least {min_val}.")
                    continue
                if max_val is not None and val > max_val:
                    print(f"  [!] Value must not exceed {max_val}.")
                    continue
                return val
            except ValueError:
                print("  [!] Invalid input. Please enter a whole number.")

    @staticmethod
    def format_fib_line(targets, res_map):
        parts = [f"Fib({n})={res_map[n]}" for n in targets]
        return ", ".join(parts)

    @classmethod
    def print_section_header(cls, title):
        print("\n" + "=" * 88)
        print(f"=== {title} ===")
        print("=" * 88)

    @classmethod
    def print_live_round(cls, round_num, targets, res_map, time_ns):
        fib_str = cls.format_fib_line(targets, res_map)
        print(f"Round {round_num:<2}: {fib_str} | T = {time_ns:,} ns", flush=True)

    @staticmethod
    def print_section_summary(label, total_ns, avg_ns):
        print("-" * 88)
        print(f"Total T ({label})   : {total_ns:,} ns")
        print(f"Average T ({label}) : {avg_ns:,} ns")

    @staticmethod
    def print_final_observation(avg_mt, avg_seq):
        print("=" * 88)
        diff_ns = abs(avg_mt - avg_seq)

        if avg_mt < avg_seq and avg_seq > 0:
            pct = ((avg_seq - avg_mt) / avg_seq) * 100
            print(f"Observation: Multithreading shortened average completion time by {diff_ns:,} ns ({pct:.2f}%).")
        elif avg_seq < avg_mt and avg_seq > 0:
            pct = ((avg_mt - avg_seq) / avg_seq) * 100
            print(f"Observation: Multithreading increased average completion time by {diff_ns:,} ns (+{pct:.2f}% overhead")
            print("             due to Python Global Interpreter Lock (GIL) serialization and thread spawning costs).")
        else:
            print("Observation: Both execution modes completed in identical average time.")
        print("=" * 88)


class ConcurrencyController:
    """
    Controller Layer: Coordinates menu selection and streams 10-round results live.
    """
    def __init__(self):
        self.model = ConcurrencyModel()
        self.view = ConcurrencyView()

    def _run_live_experiment(self, use_recursive=False):
        fib_func = (FibonacciEngine.calculate_recursive
                    if use_recursive else FibonacciEngine.calculate_iterative)
        mode_name = "Recursive O(2^n)" if use_recursive else "Iterative O(n)"
        targets = self.model.targets
        num_rounds = self.model.num_rounds

        # 1. Run and stream 10 Rounds With Multithreading
        self.view.print_section_header(f"Fibonacci Computation (With Multithreading) [{mode_name}]")
        total_mt_ns = 0
        for r in range(1, num_rounds + 1):
            t_ns, res_map = self.model.run_single_multithreaded_round(fib_func)
            total_mt_ns += t_ns
            self.view.print_live_round(r, targets, res_map, t_ns)

        avg_mt_ns = total_mt_ns // num_rounds
        self.view.print_section_summary("With Multithreading", total_mt_ns, avg_mt_ns)

        # 2. Run and stream 10 Rounds Without Multithreading (Sequential)
        self.view.print_section_header(f"Fibonacci Computation (Without Multithreading) [{mode_name}]")
        total_seq_ns = 0
        for r in range(1, num_rounds + 1):
            t_ns, res_map = self.model.run_single_sequential_round(fib_func)
            total_seq_ns += t_ns
            self.view.print_live_round(r, targets, res_map, t_ns)

        avg_seq_ns = total_seq_ns // num_rounds
        self.view.print_section_summary("Without Multithreading", total_seq_ns, avg_seq_ns)

        # 3. Print Final Observation
        self.view.print_final_observation(avg_mt_ns, avg_seq_ns)

    def run(self):
        while True:
            try:
                self.view.display_menu(self.model.targets, self.model.num_rounds)
                choice = self.view.get_int_input("Enter choice (1-3): ", min_val=1, max_val=3)

                if choice == 1:
                    self._run_live_experiment(use_recursive=False)
                elif choice == 2:
                    self._run_live_experiment(use_recursive=True)
                elif choice == 3:
                    print("\nExiting program. Goodbye!")
                    break
            except (KeyboardInterrupt, EOFError):
                print("\n\n[!] Session interrupted by user. Exiting safely. Goodbye!")
                break


if __name__ == "__main__":
    app = ConcurrencyController()
    app.run()