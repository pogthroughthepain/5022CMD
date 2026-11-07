class Graph:
    """
    Generic, reusable Unweighted Directed Graph data structure.
    Uses an adjacency list dictionary to store outgoing edges for each vertex.
    Completely decoupled from any domain entity (such as Course)
    """
    def __init__(self):
        # Dictionary mapping each vertex to a list of its outgoing adjacent vertices
        # Format: { vertex_A: [vertex_B, vertex_C], ... }
        self.adjacency_list = {}

    def addVertex(self, vertex):
        """
        Adds a new vertex to the graph if it does not already exist.
        Returns: (success, message)
        """
        if vertex is None:
            return False, "Error: Vertex cannot be None."

        if vertex in self.adjacency_list:
            return False, f"Vertex '{vertex}' already exists in the graph."

        self.adjacency_list[vertex] = []
        return True, f"Vertex '{vertex}' added successfully."

    def hasVertex(self, vertex):
        """Checks whether a vertex exists in the graph."""
        return vertex in self.adjacency_list

    def getAllVertices(self):
        """Returns a list of all vertices currently in the graph."""
        return list(self.adjacency_list.keys())

    def addEdge(self, from_vertex, to_vertex):
        """
        Creates a directed edge from 'from_vertex' -> 'to_vertex'.
        Includes edge-case validation for missing vertices, self-loops,
        duplicate edges, and circular dependencies (cycles).
        Returns: (success, message)
        """
        if from_vertex not in self.adjacency_list:
            return False, f"Error: Source vertex '{from_vertex}' does not exist."
        if to_vertex not in self.adjacency_list:
            return False, f"Error: Destination vertex '{to_vertex}' does not exist."

        # Edge Case 1: Prevent self-loop (a vertex pointing to itself)
        if from_vertex == to_vertex:
            return False, "Error: Cannot add a self-loop edge (a vertex cannot point to itself)."

        # Edge Case 2: Prevent duplicate directed edge
        if to_vertex in self.adjacency_list[from_vertex]:
            return False, f"Error: Directed edge from '{from_vertex}' to '{to_vertex}' already exists."

        # Edge Case 3: Prevent circular cycle (if to_vertex can already reach from_vertex)
        if self.hasPath(to_vertex, from_vertex):
            return False, (f"Cycle Error: Adding edge '{from_vertex} -> {to_vertex}' would create "
                           f"a circular dependency loop.")

        self.adjacency_list[from_vertex].append(to_vertex)
        return True, f"Directed edge '{from_vertex} -> {to_vertex}' added successfully."

    def removeEdge(self, from_vertex, to_vertex):
        """
        Removes an existing directed edge from 'from_vertex' -> 'to_vertex'.
        Returns: (success, message)
        """
        if from_vertex not in self.adjacency_list or to_vertex not in self.adjacency_list:
            return False, "Error: One or both vertices do not exist in the graph."

        if to_vertex not in self.adjacency_list[from_vertex]:
            return False, f"Error: No directed edge exists from '{from_vertex}' to '{to_vertex}'."

        self.adjacency_list[from_vertex].remove(to_vertex)
        return True, f"Directed edge '{from_vertex} -> {to_vertex}' removed successfully."

    def listIncomingAdjacentVertex(self, target_vertex):
        """
        Lists all vertices that have an incoming directed edge
        pointing into 'target_vertex' (i.e., u -> target_vertex).
        """
        if target_vertex not in self.adjacency_list:
            return []

        incoming_vertices = []
        for vertex, outgoing_neighbors in self.adjacency_list.items():
            if target_vertex in outgoing_neighbors:
                incoming_vertices.append(vertex)
        return incoming_vertices

    def listOutgoingAdjacentVertex(self, source_vertex):
        """
        Helper Method: Lists all vertices that 'source_vertex' has an outgoing
        directed edge pointing to (e.g., source_vertex -> v).
        Supports the feature of viewing courses unlocked by a course.
        """
        if source_vertex not in self.adjacency_list:
            return []
        return list(self.adjacency_list[source_vertex])

    def hasPath(self, start_vertex, target_vertex):
        """
        QoL Helper: Uses Breadth-First Search (BFS) to check if a directed path
        exists from 'start_vertex' to 'target_vertex'. Used to prevent cycles.
        """
        if start_vertex not in self.adjacency_list or target_vertex not in self.adjacency_list:
            return False

        visited = set()
        queue = [start_vertex]

        while queue:
            current = queue.pop(0)
            if current == target_vertex:
                return True
            if current not in visited:
                visited.add(current)
                for neighbor in self.adjacency_list[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        return False