import threading
import time


class ConcurrencyModel:
    """
    Model Layer: Executes the 3-task Fibonacci workload (35, 38, 40) across
    10 rounds both with multithreading (3 separate threads) and sequentially
    without multithreading, measuring time in nanoseconds.
    """
    DEFAULT_TARGETS = [35, 38, 40]
    DEFAULT_ROUNDS = 10

    def __init__(self):
        self.targets = list(self.DEFAULT_TARGETS)
        self.num_rounds = self.DEFAULT_ROUNDS

    @staticmethod
    def _thread_worker(n, fib_func, results_dict, start_times, end_times, lock):
        """
        Worker target executed by each individual thread.
        Records the exact nanosecond start time (t_start) and end time (t_end)
        so total elapsed time follows:
        T = End_Time_Of_Thread_Finished_Last - Start_Time_Of_Thread_That_Started_First
        """
        t_start = time.perf_counter_ns()
        fib_val = fib_func(n)
        t_end = time.perf_counter_ns()

        with lock:
            start_times.append(t_start)
            end_times.append(t_end)
            results_dict[n] = fib_val

    def run_single_multithreaded_round(self, fib_func):
        """
        Creates 3 separate threads (one for Fib(35), one for Fib(38), one for Fib(40)).
        Returns: (elapsed_ns, results_dict)
        """
        threads = []
        results_dict = {}
        start_times = []
        end_times = []
        lock = threading.Lock()

        for n_val in self.targets:
            thread = threading.Thread(
                target=self._thread_worker,
                args=(n_val, fib_func, results_dict, start_times, end_times, lock)
            )
            threads.append(thread)

        # Start all 3 threads
        for thread in threads:
            thread.start()

        # Wait for all 3 threads to complete execution
        for thread in threads:
            thread.join()

        t1_first_start = min(start_times)
        t2_last_end = max(end_times)
        elapsed_ns = t2_last_end - t1_first_start

        return elapsed_ns, results_dict

    def run_single_sequential_round(self, fib_func):
        """
        Calculates Fib(35), Fib(38), and Fib(40) sequentially without multithreading.
        Returns: (elapsed_ns, results_dict)
        """
        results_dict = {}
        t1_start = time.perf_counter_ns()

        for n_val in self.targets:
            results_dict[n_val] = fib_func(n_val)

        t2_end = time.perf_counter_ns()
        elapsed_ns = t2_end - t1_start

        return elapsed_ns, results_dict