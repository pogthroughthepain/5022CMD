from model import Product, InventoryModel


class InventoryView:
    """
    View Layer: Handles all CLI menus, formatted tables, and validated user inputs.
    """

    @staticmethod
    def display_menu(load_factor, active_count, capacity):
        print("\n" + "=" * 54)
        print("           === Pharmacy Inventory System ===          ")
        print(f"           [Table Load: {active_count}/{capacity} slots ({load_factor * 100:.1f}%)]")
        print("=" * 54)
        print("1. Insert Product")
        print("2. Search Product")
        print("3. Edit Product Details")
        print("4. Delete Product")
        print("5. View All Active Inventory")
        print("6. Inspect Hash Table Slots")
        print("7. Run 5,000-Record Benchmark")
        print("8. Exit")
        print("-" * 54)

    @staticmethod
    def get_int_input(prompt, min_val=None, max_val=None, allow_empty=False, default_val=None):
        """Safely reads an integer from the user, preventing ValueError crashes."""
        while True:
            raw = input(prompt).strip()
            if allow_empty and raw == "":
                return default_val
            try:
                val = int(raw)
                if min_val is not None and val < min_val:
                    print(f"  [!] Input must be at least {min_val}.")
                    continue
                if max_val is not None and val > max_val:
                    print(f"  [!] Input must not exceed {max_val}.")
                    continue
                return val
            except ValueError:
                print("  [!] Invalid input. Please enter a whole number (integer).")

    @staticmethod
    def get_float_input(prompt, min_val=0.0, allow_empty=False, default_val=None):
        """Safely reads a float (e.g., price) from the user."""
        while True:
            raw = input(prompt).strip()
            if allow_empty and raw == "":
                return default_val
            try:
                val = float(raw)
                if min_val is not None and val < min_val:
                    print(f"  [!] Value cannot be less than {min_val:.2f}.")
                    continue
                return val
            except ValueError:
                print("  [!] Invalid input. Please enter a valid numeric value (e.g., 5.90).")

    @staticmethod
    def get_string_input(prompt, allow_empty=False, default_val=None):
        """Safely reads a non-empty string from the user."""
        while True:
            raw = input(prompt).strip()
            if allow_empty and raw == "":
                return default_val
            if len(raw) == 0:
                print("  [!] Input cannot be empty.")
                continue
            return raw

    @staticmethod
    def display_search_result(result, searched_id):
        """Displays search output matching the assignment brief format plus probe analytics."""
        print("-" * 54)
        if result["found"]:
            prod = result["product"]
            print("Product Found!")
            print(f"ID: {prod.product_id} | Name: {prod.name} | Category: {prod.category} "
                  f"| Price: RM{prod.price:.2f} | Stock: {prod.stock}")
            print(f"Hash Table Location : Slot [{result['ht_slot']}] (Probes: {result['ht_probes']})")
            print(f"1D Array Location   : Index [{result['arr_idx']}] (Comparisons: {result['arr_comparisons']})")
        else:
            print(f"Product ID '{searched_id}' Not Found!")
            print(f"Hash Table Probes Made  : {result['ht_probes']}")
            print(f"1D Array Comparisons    : {result['arr_comparisons']}")

        print(f"\nSearch completed in {result['ht_time']:.6f} seconds (Hash Table)")
        print(f"Search completed in {result['arr_time']:.6f} seconds (Array - same record)")
        print("-" * 54)

    @staticmethod
    def display_all_products(products):
        if not products:
            print("\n  [i] The inventory is currently empty.")
            return

        print("\n" + "-" * 72)
        print(f"{'ID':<8} | {'Product Name':<24} | {'Category':<15} | {'Price (RM)':<10} | {'Stock':<6}")
        print("-" * 72)
        for p in products:
            print(f"{p.product_id:<8} | {p.name:<24} | {p.category:<15} | {p.price:<10.2f} | {p.stock:<6}")
        print("-" * 72)
        print(f"Total Active Products: {len(products)}")

    @staticmethod
    def display_hash_table_state(table_state):
        print("\n" + "=" * 78)
        print(f"{'Slot':<6} | {'Status':<11} | {'Key (ID)':<10} | {'Home Slot':<10} | {'Product Details'}")
        print("=" * 78)
        for slot_idx, status, key, home_slot, prod in table_state:
            if status == "EMPTY":
                print(f"[{slot_idx:<3}]  | {'EMPTY':<11} | {'-':<10} | {'-':<10} | -")
            elif status == "TOMBSTONE":
                print(
                    f"[{slot_idx:<3}]  | {'TOMBSTONE':<11} | {str(key):<10} | [{home_slot:<2}]       | <Deleted Record - Probe Chain Preserved>")
            else:
                collision_note = " (Probed!)" if slot_idx != home_slot else ""
                details = f"{prod.name} (RM{prod.price:.2f}, Qty: {prod.stock}){collision_note}"
                print(f"[{slot_idx:<3}]  | {'OCCUPIED':<11} | {str(key):<10} | [{home_slot:<2}]       | {details}")
        print("=" * 78)

    @staticmethod
    def display_benchmark_results(dataset_size, table_capacity, results):
        print("\n" + "=" * 125)
        print(
            f"  PERFORMANCE BENCHMARK: {dataset_size} Records (Hash Table Capacity: {table_capacity}, Averaged over 1,000 runs)")
        print("=" * 125)
        print(
            f"{'Search Scenario':<42} | {'HT Probes':<9} | {'HT Time (s)':<14} | {'Arr Comp.':<9} | {'Arr Time (s)':<14} | {'Speedup'}")
        print("-" * 125)
        for r in results:
            print(f"{r['scenario']:<42} | {r['ht_probes']:<9} | {r['ht_time']:<14.8f} | "
                  f"{r['arr_comparisons']:<9} | {r['arr_time']:<14.8f} | {r['speedup']:.1f}x faster")
        print("=" * 125)


class InventoryController:
    """
    Controller Layer: Connects user actions from InventoryView to InventoryModel.
    """

    def __init__(self):
        self.model = InventoryModel(table_size=19)
        self.view = InventoryView()

    def run(self):
        while True:
            try:
                ht = self.model.hash_table
                self.view.display_menu(ht.load_factor(), ht.count, ht.size)
                choice = self.view.get_int_input("Enter choice (1-8): ", min_val=1, max_val=8)

                if choice == 1:
                    self._handle_insert()
                elif choice == 2:
                    self._handle_search()
                elif choice == 3:
                    self._handle_edit()
                elif choice == 4:
                    self._handle_delete()
                elif choice == 5:
                    self._handle_view_all()
                elif choice == 6:
                    self._handle_inspect_table()
                elif choice == 7:
                    self._handle_benchmark()
                elif choice == 8:
                    print("\nExiting Inventory System. Goodbye!")
                    break
            except (KeyboardInterrupt, EOFError):
                print("\n\n[!] Session interrupted by user. Exiting safely. Goodbye!")
                break

    def _handle_insert(self):
        print("\n--- Insert New Pharmacy Product ---")
        # Quick pre-check if table is already at 100% capacity
        if self.model.hash_table.count >= self.model.hash_table.size:
            print("  [!] Error: Hash Table is currently full. Delete a record before inserting.")
            return

        pid = self.view.get_int_input("Enter Product ID (positive integer): ", min_val=1)

        # Check if ID already exists before asking for the rest of the fields (QoL)
        existing_prod, existing_slot, _ = self.model.hash_table.search(pid)
        if existing_prod is not None:
            print(
                f"  [!] Duplicate Error: Product ID {pid} already exists at slot [{existing_slot}] ({existing_prod.name}).")
            return

        name = self.view.get_string_input("Enter Product Name: ")
        category = self.view.get_string_input("Enter Category (or press Enter for 'General'): ",
                                              allow_empty=True, default_val="General")
        price = self.view.get_float_input("Enter Price (RM): ", min_val=0.01)
        stock = self.view.get_int_input("Enter Stock Quantity: ", min_val=0)

        new_product = Product(pid, name, category, price, stock)
        success, slot_idx, probes, message = self.model.insert_product(new_product)
        print(f"\n{message} (Probes required: {probes})")

    def _handle_search(self):
        print("\n--- Search Product ---")
        pid = self.view.get_int_input("Enter Product ID to search: ", min_val=1)
        result = self.model.search_and_compare(pid)
        self.view.display_search_result(result, pid)

    def _handle_edit(self):
        print("\n--- Edit Existing Product ---")
        pid = self.view.get_int_input("Enter Product ID to edit: ", min_val=1)
        existing_prod, slot_idx, _ = self.model.hash_table.search(pid)

        if existing_prod is None:
            print(f"  [!] Product ID {pid} not found in the inventory.")
            return

        print(f"Current Record at slot [{slot_idx}]: {existing_prod}")
        print("(Press Enter on any field to keep its current value)")

        new_name = self.view.get_string_input(f"New Name [{existing_prod.name}]: ",
                                              allow_empty=True, default_val=existing_prod.name)
        new_cat = self.view.get_string_input(f"New Category [{existing_prod.category}]: ",
                                             allow_empty=True, default_val=existing_prod.category)
        new_price = self.view.get_float_input(f"New Price (RM) [{existing_prod.price:.2f}]: ",
                                              min_val=0.01, allow_empty=True, default_val=existing_prod.price)
        new_stock = self.view.get_int_input(f"New Stock Quantity [{existing_prod.stock}]: ",
                                            min_val=0, allow_empty=True, default_val=existing_prod.stock)

        success, _, probes, message = self.model.edit_product(pid, new_name, new_cat, new_price, new_stock)
        print(f"\n{message} (Probes: {probes})")

    def _handle_delete(self):
        print("\n--- Delete Product (Lazy Deletion / Tombstone) ---")
        pid = self.view.get_int_input("Enter Product ID to delete: ", min_val=1)
        success, slot_idx, probes, message = self.model.delete_product(pid)
        print(f"\n{message} (Probes: {probes})")

    def _handle_view_all(self):
        products = self.model.get_all_products()
        self.view.display_all_products(products)

    def _handle_inspect_table(self):
        state = self.model.hash_table.get_table_state()
        self.view.display_hash_table_state(state)

    def _handle_benchmark(self):
        print("\nRunning 5,000-record search benchmark (1,000 iterations per scenario)...")
        size, cap, results = self.model.run_benchmark_experiment()
        self.view.display_benchmark_results(size, cap, results)


if __name__ == "__main__":
    app = InventoryController()
    app.run()