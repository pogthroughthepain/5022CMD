class HashEntry:
    """
    Represents a single slot/bucket in the Hash Table.
    Bundles the key, value, and tombstone status together into one object.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.is_deleted = False  # True means this slot is a Tombstone (deleted)

class HashTable:
    """
    Generic, reusable Hash Table using Open Addressing with Linear Probing.
    Kept free of domain-specific logic so it can store any entity type.
    """
    def __init__(self, size=53):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Hash table size must be a positive integer.")

        self.size = size
        self.slots = [None] * self.size
        self.count = 0  # Tracks number of active (non deleted) items

    def _hash(self, key):
        """
        Calculates the home index for a key.
        Uses modulo for integers (like Product ID 1042) and ASCII sum for strings.
        """
        if isinstance(key, int):
            return abs(key) % self.size

        # Fallback for string keys (same logic as hash_string in the lab)
        total = sum(ord(char) for char in str(key))
        return total % self.size

    def load_factor(self):
        """Returns the current load factor (active items / total slots)."""
        return self.count / self.size

    def insert(self, key, value):
        """
        Inserts a key-value pair using Linear Probing.
        Prevents duplicate keys and recycles Tombstone slots when possible.
        Returns: (success, slot_index, probes, message)
        """
        if key is None:
            return False, -1, 0, "Error: Key cannot be None."

        home_idx = self._hash(key)
        first_tombstone_idx = None
        probes = 0

        for step in range(self.size):
            idx = (home_idx + step) % self.size
            probes += 1
            entry = self.slots[idx]

            # Case 1: Hit a never-used slot (end of probe chain)
            if entry is None:
                # Recycle the earliest tombstone we passed, or use this empty slot
                target_idx = first_tombstone_idx if first_tombstone_idx is not None else idx
                self.slots[target_idx] = HashEntry(key, value)
                self.count += 1
                return True, target_idx, probes, f"Product inserted successfully into slot [{target_idx}]"

            # Case 2: Slot has an active item then check if it's a duplicate key
            if not entry.is_deleted:
                if entry.key == key:
                    return False, idx, probes, f"Duplicate Error: Key '{key}' already exists at slot [{idx}]."

            # Case 3: Slot is a Tombstone — remember the first one we see, but keep probing
            # to make sure the key doesn't already exist further down the chain!
            else:
                if first_tombstone_idx is None:
                    first_tombstone_idx = idx

        # If the loop checked every slot and found no 'None', we can still use a tombstone if we saw one
        if first_tombstone_idx is not None:
            self.slots[first_tombstone_idx] = HashEntry(key, value)
            self.count += 1
            return True, first_tombstone_idx, probes, f"Product inserted into recycled slot [{first_tombstone_idx}]"

        return False, -1, probes, "Error: Hash Table is completely full."

    def search(self, key):
        """
        Searches for a key using Linear Probing.
        Returns: (value, slot_index, probes) -> value is None and slot_index is -1 if not found.
        """
        if key is None:
            return None, -1, 0

        home_idx = self._hash(key)
        probes = 0

        for step in range(self.size):
            idx = (home_idx + step) % self.size
            probes += 1
            entry = self.slots[idx]

            # If we hit None, the key was never inserted down this chain
            if entry is None:
                return None, -1, probes

            # If we find the matching key and it hasn't been deleted, return it
            if not entry.is_deleted and entry.key == key:
                return entry.value, idx, probes

            # Otherwise (collision or Tombstone), keep probing to the next slot

        return None, -1, probes

    def edit(self, key, new_value):
        """
        Updates the value for an existing active key.
        Returns: (success, slot_index, probes, message)
        """
        _, idx, probes = self.search(key)
        if idx == -1:
            return False, -1, probes, f"Key '{key}' not found."

        self.slots[idx].value = new_value
        return True, idx, probes, f"Record at slot [{idx}] updated successfully."

    def delete(self, key):
        """
        Deletes a key using Lazy Deletion (marks the slot as a Tombstone).
        Returns: (success, slot_index, probes, message)
        """
        _, idx, probes = self.search(key)
        if idx == -1:
            return False, -1, probes, f"Key '{key}' not found."

        self.slots[idx].is_deleted = True
        self.slots[idx].value = None  # Free up the product object reference (saves memory!)
        self.count -= 1
        return True, idx, probes, f"Record at slot [{idx}] deleted (marked as Tombstone)."

    def get_table_state(self):
        """
        QoL helper: Returns a list of slot details so the View can display
        the internal table layout (Occupied, Empty, and Tombstone slots).
        """
        state = []
        for idx, entry in enumerate(self.slots):
            if entry is None:
                state.append((idx, "EMPTY", None, None, None))
            elif entry.is_deleted:
                state.append((idx, "TOMBSTONE", entry.key, self._hash(entry.key), None))
            else:
                state.append((idx, "OCCUPIED", entry.key, self._hash(entry.key), entry.value))
        return state