def _fast_recursive_fib(n):
    """
    Standalone recursive helper to avoid class-method lookup overhead
    across hundreds of millions of recursive calls.
    """
    if n <= 1:
        return n
    return _fast_recursive_fib(n - 1) + _fast_recursive_fib(n - 2)


class FibonacciEngine:
    """
    Algorithm Layer: Provides isolated functions to compute the n-th Fibonacci number.
    Kept completely separate from threading and UI logic for clean abstraction.
    """
    @staticmethod
    def calculate_iterative(n):
        """
        Calculates the n-th Fibonacci number iteratively in O(n) linear time.
        Primitive Operation Count Derivation:
        - Base case check (n <= 1): 1 comparison -> O(1)
        - Initialization (a = 0, b = 1): 2 assignments -> O(1)
        - Loop runs (n - 1) times: each iteration performs 1 addition and 2 assignments
        - Total Primitive Operations T(n) = 4n + 1 -> Big-O Time Complexity is O(n).
        """
        if n <= 0:
            return 0
        if n == 1:
            return 1

        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    @staticmethod
    def calculate_recursive(n):
        """
        Calculates the n-th Fibonacci number using binary recursion in O(2^n) exponential time.
        """
        if n <= 0:
            return 0
        return _fast_recursive_fib(n)