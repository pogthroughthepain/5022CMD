import time
from hash_table import HashTable


class Product:
    """
    Entity class representing a product in the pharmacy retail outlet.
    Attributes and types are chosen to reflect real-world pharmacy inventory needs:
    - product_id (int): Unique numeric identifier, ideal for fast modulo hashing.
    - name (str): Medication or product name including dosage.
    - category (str): Classification (e.g., Analgesic, Antibiotic, Supplement).
    - price (float): Retail unit price in RM (supports decimal values).
    - stock (int): Current physical quantity in whole units.
    """
    def __init__(self, product_id, name, category, price, stock):
        self.product_id = int(product_id)
        self.name = str(name).strip()
        self.category = str(category).strip()
        self.price = float(price)
        self.stock = int(stock)

    def __str__(self):
        return (f"ID: {self.product_id} | Name: {self.name} | "
                f"Category: {self.category} | Price: RM{self.price:.2f} | Stock: {self.stock}")


class InventoryModel:
    """
    Manages both the Hash Table and the 1D Array (Python list) to keep them
    synchronized for CRUD operations and search performance comparisons.
    """
    def __init__(self, table_size=19):
        # Prime size 19 is compact enough to display on screen while demonstrating probing
        self.hash_table = HashTable(size=table_size)
        self.array_storage = []  # 1D array for performance comparison
        self._load_predefined_records()

    def _load_predefined_records(self):
        """
        Pre-populates the pharmacy inventory with 10 initial records.
        Note: IDs 1042, 1061, and 1080 all hash to slot [16] when table_size=19
        (since 1042 % 19 == 16, 1061 % 19 == 16, 1080 % 19 == 16),
        intentionally demonstrating Open Addressing with Linear Probing.
        """
        initial_products = [
            Product(1042, "Paracetamol 500mg", "Analgesic", 5.90, 120),
            Product(1005, "Amoxicillin 250mg", "Antibiotic", 18.50, 45),
            Product(1061, "Ibuprofen 400mg", "Analgesic", 8.20, 85),      # Collides with 1042 -> probes to [17]
            Product(1012, "Cetirizine 10mg", "Antihistamine", 12.00, 60),
            Product(1080, "Aspirin 100mg", "Analgesic", 6.50, 95),         # Collides with 1042 & 1061 -> probes to [18]
            Product(1028, "Vitamin C 1000mg", "Supplement", 35.00, 150),
            Product(1033, "Omeprazole 20mg", "Antacid", 22.90, 40),
            Product(1050, "Loratadine 10mg", "Antihistamine", 14.50, 70),
            Product(1074, "Metformin 500mg", "Antidiabetic", 16.80, 110),
            Product(1099, "Cough Syrup 120ml", "Cold & Flu", 11.40, 55),
        ]

        for product in initial_products:
            self.insert_product(product)

    def insert_product(self, product):
        """
        Inserts a Product into both the Hash Table and the 1D Array.
        Returns: (success, slot_index, probes, message)
        """
        success, slot_idx, probes, message = self.hash_table.insert(product.product_id, product)
        if success:
            self.array_storage.append(product)
        return success, slot_idx, probes, message

    def search_in_array(self, product_id):
        """
        Performs a standard Linear Search O(n) through the 1D array.
        Returns: (Product or None, index_or_-1, comparisons_made)
        """
        comparisons = 0
        for idx, product in enumerate(self.array_storage):
            comparisons += 1
            if product.product_id == product_id:
                return product, idx, comparisons
        return None, -1, comparisons

    def search_and_compare(self, product_id):
        """
        Searches for a product_id in both the Hash Table and the 1D Array,
        measuring the exact execution time of each using time.perf_counter().
        """
        # 1. Measure Hash Table Search Time
        start_ht = time.perf_counter()
        ht_product, ht_slot, ht_probes = self.hash_table.search(product_id)
        ht_time = time.perf_counter() - start_ht

        # 2. Measure 1D Array Linear Search Time
        start_arr = time.perf_counter()
        arr_product, arr_idx, arr_comparisons = self.search_in_array(product_id)
        arr_time = time.perf_counter() - start_arr

        return {
            "found": ht_product is not None,
            "product": ht_product,
            "ht_slot": ht_slot,
            "ht_probes": ht_probes,
            "ht_time": ht_time,
            "arr_idx": arr_idx,
            "arr_comparisons": arr_comparisons,
            "arr_time": arr_time
        }

    def edit_product(self, product_id, new_name, new_category, new_price, new_stock):
        """
        Updates an existing product's details in both the Hash Table and 1D Array.
        """
        existing_product, slot_idx, probes = self.hash_table.search(product_id)
        if existing_product is None:
            return False, -1, probes, f"Product ID {product_id} not found."

        # Update attributes in-place (since both structures hold a reference to this object,
        # updating the object updates both, and calling edit() verifies Hash Table update logic)
        existing_product.name = str(new_name).strip()
        existing_product.category = str(new_category).strip()
        existing_product.price = float(new_price)
        existing_product.stock = int(new_stock)

        return self.hash_table.edit(product_id, existing_product)

    def delete_product(self, product_id):
        """
        Deletes a product from both the Hash Table (Tombstone) and the 1D Array.
        """
        success, slot_idx, probes, message = self.hash_table.delete(product_id)
        if success:
            # Also remove from the 1D array so both stay synchronized
            for i, prod in enumerate(self.array_storage):
                if prod.product_id == product_id:
                    self.array_storage.pop(i)
                    break
        return success, slot_idx, probes, message

    def get_all_products(self):
        """Returns a list of all active products currently in the inventory."""
        return list(self.array_storage)

    def run_benchmark_experiment(self, dataset_size=5000, table_capacity=10007):
        """
        QoL Feature for Report:
        Creates a temporary large dataset (e.g., 5,000 records in a prime-sized table of 10,007)
        to compare Hash Table O(1) vs 1D Array O(n) across Best, Average, Worst, and Missing cases.
        """
        temp_ht = HashTable(size=table_capacity)
        temp_arr = []

        # Populate both structures with identical synthetic pharmacy records
        for i in range(dataset_size):
            pid = 10000 + (i * 3)  # Spread out product IDs
            prod = Product(pid, f"Medicine_{i}", "General", 10.0, 50)
            temp_ht.insert(pid, prod)
            temp_arr.append(prod)

        test_cases = [
            ("First Record (Best Case for Array)", temp_arr[0].product_id),
            ("Middle Record (Average Case)", temp_arr[dataset_size // 2].product_id),
            ("Last Record (Worst Case for Array)", temp_arr[-1].product_id),
            ("Non-Existent ID (Worst Case Unsuccessful)", 9999999)
        ]

        results = []
        iterations = 1000  # Average over 1,000 runs to eliminate OS background noise

        for label, target_id in test_cases:
            # Benchmark Hash Table
            t0 = time.perf_counter()
            for _ in range(iterations):
                _, ht_slot, ht_probes = temp_ht.search(target_id)
            ht_avg_time = (time.perf_counter() - t0) / iterations

            # Benchmark 1D Array
            t1 = time.perf_counter()
            for _ in range(iterations):
                arr_comp = 0
                for item in temp_arr:
                    arr_comp += 1
                    if item.product_id == target_id:
                        break
            arr_avg_time = (time.perf_counter() - t1) / iterations

            speedup = arr_avg_time / ht_avg_time if ht_avg_time > 0 else 0.0
            results.append({
                "scenario": label,
                "target_id": target_id,
                "ht_probes": ht_probes,
                "ht_time": ht_avg_time,
                "arr_comparisons": arr_comp,
                "arr_time": arr_avg_time,
                "speedup": speedup
            })

        return dataset_size, table_capacity, results