from graph import Graph

class Course:
    """
    Domain / Entity class representing a single university course.
    Implements __eq__ and __hash__ so Course instances can be stored
    directly as generic vertex objects inside the Graph data structure.
    """
    def __init__(self, course_code, course_name, credit_hours, level, semester):
        self.course_code = str(course_code).strip().upper()
        self.course_name = str(course_name).strip()
        self.credit_hours = int(credit_hours)
        # Normalizes level to either "Core" or "Elective"
        self.level = str(level).strip().capitalize()
        self.semester = int(semester)

    def get_profile(self, respect_visibility=False):
        """
        Returns a formatted profile string for the course.
        - If respect_visibility is False: shows all details.
        - If respect_visibility is True: hides details for Elective courses.
        """
        if respect_visibility and self.level.lower() == "elective":
            return (f"Course Name  : {self.course_name}\n"
                    f"Visibility   : [Elective Course - Other details are hidden]")

        return (f"Course Code  : {self.course_code}\n"
                f"Course Name  : {self.course_name}\n"
                f"Credit Hours : {self.credit_hours}\n"
                f"Course Level : {self.level}\n"
                f"Semester     : Year {(self.semester - 1) // 2 + 1}, Semester {self.semester}")

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.course_code == other.course_code
        return False

    def __hash__(self):
        return hash(self.course_code)

    def __str__(self):
        return f"{self.course_code} ({self.course_name})"


class PrerequisiteModel:
    """
    Model Layer: Manages the University Course Prerequisite System using the generic Graph.
    Enforces the assignment constraint of minimum 5 and maximum 10 courses.
    """
    MIN_COURSES = 5
    MAX_COURSES = 10

    def __init__(self):
        self.graph = Graph()
        # Lookup helper mapping course_code string -> Course vertex object
        self.course_lookup = {}
        self._load_predefined_courses()

    def _load_predefined_courses(self):
        """
        Initializes 6 predefined courses (4 Core, 2 Elective) and establishes
        realistic prerequisite directed edges (Prerequisite Y -> Target Course X).
        """
        initial_courses = [
            Course("CS101", "Introduction to Programming", 4, "Core", 1),
            Course("CS201", "Data Structures", 4, "Core", 2),
            Course("CS301", "Advanced Algorithms", 4, "Core", 3),
            Course("CS302", "Database Systems", 3, "Core", 3),
            Course("CS401", "Software Engineering", 4, "Elective", 4),
            Course("CS402", "Artificial Intelligence", 3, "Elective", 4),
        ]

        for course in initial_courses:
            self.add_course(course)

        # Define prerequisite relationships: (Prerequisite_Code, Target_Course_Code)
        # Edge direction: Prerequisite_Y ---> Target_Course_X
        initial_prerequisites = [
            ("CS101", "CS201"),  # CS101 unlocks CS201
            ("CS101", "CS301"),  # CS101 is also a direct prerequisite for CS301
            ("CS201", "CS301"),  # CS201 unlocks CS301
            ("CS201", "CS302"),  # CS201 unlocks CS302
            ("CS301", "CS401"),  # CS301 unlocks CS401
            ("CS302", "CS401"),  # CS302 unlocks CS401
            ("CS301", "CS402"),  # CS301 unlocks CS402
        ]

        for prereq_code, target_code in initial_prerequisites:
            self.add_prerequisite(target_code, prereq_code)

    def get_course(self, course_code):
        """Retrieves the Course object for a given course code (case-insensitive)."""
        if not course_code:
            return None
        return self.course_lookup.get(str(course_code).strip().upper())

    def get_all_courses(self):
        """Returns all Course vertex objects in the graph."""
        return self.graph.getAllVertices()

    def get_prerequisites_for_course(self, course_code):
        """
        Lists all prerequisite courses required by a course.
        Calls Graph.listIncomingAdjacentVertex(target_course).
        """
        target_course = self.get_course(course_code)
        if target_course is None:
            return None
        return self.graph.listIncomingAdjacentVertex(target_course)

    def get_courses_unlocked_by(self, course_code):
        """
        Lists all courses that a particular course unlocks.
        Calls Graph.listOutgoingAdjacentVertex(source_course).
        """
        source_course = self.get_course(course_code)
        if source_course is None:
            return None
        return self.graph.listOutgoingAdjacentVertex(source_course)

    def add_course(self, new_course):
        """
        Adds a new Course vertex on-demand into the graph.
        Enforces the maximum limit of 10 courses specified in the assignment brief.
        Returns: (success, message)
        """
        if len(self.course_lookup) >= self.MAX_COURSES:
            return False, (f"Limit Reached: Cannot exceed the maximum of {self.MAX_COURSES} courses "
                           f"currently in the system.")

        if new_course.course_code in self.course_lookup:
            return False, f"Duplicate Error: Course '{new_course.course_code}' already exists."

        success, msg = self.graph.addVertex(new_course)
        if success:
            self.course_lookup[new_course.course_code] = new_course
            return True, f"Course '{new_course}' added to the graph successfully."
        return False, msg

    def add_prerequisite(self, target_code_x, prereq_code_y):
        """
        Allows Course X to add Course Y as a prerequisite on-demand.
        Creates an incoming directed edge from Y -> X in the graph.
        Returns: (success, message)
        """
        course_x = self.get_course(target_code_x)
        course_y = self.get_course(prereq_code_y)

        if course_x is None:
            return False, f"Error: Target course '{target_code_x}' does not exist."
        if course_y is None:
            return False, f"Error: Prerequisite course '{prereq_code_y}' does not exist."

        if course_x == course_y:
            return False, "Error: A course cannot be a prerequisite for itself."

        # Create directed edge from Y (prerequisite) -> X (target course)
        success, msg = self.graph.addEdge(course_y, course_x)
        if success:
            return True, f"Prerequisite added: '{course_y}' is now required for '{course_x}'."
        return False, msg

    def remove_prerequisite(self, target_code_x, prereq_code_y):
        """
        Allows Course X to remove Course Y as a prerequisite on-demand.
        Removes the directed edge from Y -> X in the graph.
        Returns: (success, message)
        """
        course_x = self.get_course(target_code_x)
        course_y = self.get_course(prereq_code_y)

        if course_x is None:
            return False, f"Error: Target course '{target_code_x}' does not exist."
        if course_y is None:
            return False, f"Error: Prerequisite course '{prereq_code_y}' does not exist."

        success, msg = self.graph.removeEdge(course_y, course_x)
        if success:
            return True, f"Prerequisite removed: '{course_y}' is no longer required for '{course_x}'."
        return False, msg