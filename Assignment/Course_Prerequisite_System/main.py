from course_model import Course, PrerequisiteModel


class CourseView:
    """
    View Layer: Handles all CLI menus, formatted course outputs, and validated user inputs.
    """
    @staticmethod
    def display_menu(current_count, max_count):
        print("\n" + "=" * 60)
        print("      ==== University Course Prerequisite System ====       ")
        print(f"        [Registered Courses: {current_count}/{max_count} (Min: 5, Max: 10)]")
        print("=" * 60)
        print("  1. View All Courses")
        print("  2. View Course Details (Full Details - Ignores Level)")
        print("  3. View Prerequisites of a Course (Incoming Edges)")
        print("  4. View Courses Unlocked by a Course (Outgoing Edges)")
        print("  5. Add a New Course On-Demand (New Vertex)")
        print("  6. View Course Profile by Level (Hides Elective Details)")
        print("  7. Add Prerequisite On-Demand (New Edge Y -> X)")
        print("  8. Remove Prerequisite On-Demand (Remove Edge Y -> X)")
        print("  9. Inspect Complete Graph Adjacency Structure")
        print(" 10. Exit")
        print("-" * 60)

    @staticmethod
    def get_int_input(prompt, min_val=None, max_val=None):
        """Safely reads an integer within [min_val, max_val]."""
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
    def get_string_input(prompt):
        """Safely reads a non-empty string."""
        while True:
            raw = input(prompt).strip()
            if len(raw) == 0:
                print("  [!] Input cannot be empty.")
                continue
            return raw

    @staticmethod
    def get_level_input(prompt):
        """Safely reads and validates 'Core' or 'Elective'."""
        while True:
            raw = input(prompt).strip().capitalize()
            if raw in ("Core", "Elective"):
                return raw
            print("  [!] Invalid course level. Please enter 'Core' or 'Elective'.")

    @staticmethod
    def display_all_courses(courses):
        """Displays a list of all courses."""
        if not courses:
            print("\n  [i] No courses are currently registered in the graph.")
            return

        print("\nAvailable Courses:")
        print("-" * 60)
        for idx, course in enumerate(courses, start=1):
            print(f"{idx}. {course.course_code:<8} {course.course_name:<32} [{course.level}]")
        print("-" * 60)

    @staticmethod
    def display_course_profile(course, respect_visibility=False):
        """Displays either full course details (Mandatory 5b) or visibility-filtered details (Advanced 5b)."""
        print("\n" + "-" * 50)
        if respect_visibility:
            print("  [Course Profile - Level Visibility Active]")
        else:
            print("  [Course Details - Full Administrative View]")
        print("-" * 50)
        print(course.get_profile(respect_visibility=respect_visibility))
        print("-" * 50)

    @staticmethod
    def display_prerequisites(target_course, prerequisites):
        """Displays all incoming prerequisite vertices for target_course."""
        print(f"\nPrerequisites for {target_course.course_code} {target_course.course_name}:")
        if not prerequisites:
            print("  - None (This course has no prerequisites)")
        else:
            for prereq in prerequisites:
                print(f"  - {prereq.course_code} ({prereq.course_name})")

    @staticmethod
    def display_unlocked_courses(source_course, unlocked_courses):
        """Displays all outgoing courses unlocked by source_course."""
        print(f"\nCourses unlocked by {source_course.course_code} {source_course.course_name}:")
        if not unlocked_courses:
            print("  - None (This course does not unlock any subsequent courses)")
        else:
            for unlocked in unlocked_courses:
                print(f"  - {unlocked.course_code} ({unlocked.course_name})")

    @staticmethod
    def display_graph_structure(model):
        """QoL Feature: Displays every vertex with both its Incoming (Prerequisites) and Outgoing (Unlocked) edges."""
        courses = model.get_all_courses()
        print("\n" + "=" * 82)
        print(f"{'Vertex (Course)':<28} | {'Incoming Edges (Prereqs)':<24} | {'Outgoing Edges (Unlocks)'}")
        print("=" * 82)
        for c in courses:
            incoming = [p.course_code for p in model.get_prerequisites_for_course(c.course_code)]
            outgoing = [u.course_code for u in model.get_courses_unlocked_by(c.course_code)]
            in_str = ", ".join(incoming) if incoming else "None"
            out_str = ", ".join(outgoing) if outgoing else "None"
            label = f"{c.course_code}: {c.course_name[:18]}"
            print(f"{label:<28} | {in_str:<24} | {out_str}")
        print("=" * 82)


class CourseController:
    """
    Controller Layer: Connects CourseView inputs to PrerequisiteModel and Graph operations.
    """
    def __init__(self):
        self.model = PrerequisiteModel()
        self.view = CourseView()

    def run(self):
        while True:
            try:
                current_count = len(self.model.get_all_courses())
                self.view.display_menu(current_count, self.model.MAX_COURSES)
                choice = self.view.get_int_input("Enter choice (1-10): ", min_val=1, max_val=10)

                if choice == 1:
                    self._handle_view_all_courses()
                elif choice == 2:
                    self._handle_view_course_details(respect_visibility=False)
                elif choice == 3:
                    self._handle_view_prerequisites()
                elif choice == 4:
                    self._handle_view_unlocked_courses()
                elif choice == 5:
                    self._handle_add_course_on_demand()
                elif choice == 6:
                    self._handle_view_course_details(respect_visibility=True)
                elif choice == 7:
                    self._handle_add_prerequisite_on_demand()
                elif choice == 8:
                    self._handle_remove_prerequisite_on_demand()
                elif choice == 9:
                    self.view.display_graph_structure(self.model)
                elif choice == 10:
                    print("\nExiting program. Goodbye!")
                    break
            except (KeyboardInterrupt, EOFError):
                print("\n\n[!] Session interrupted by user. Exiting safely. Goodbye!")
                break

    def _handle_view_all_courses(self):
        courses = self.model.get_all_courses()
        self.view.display_all_courses(courses)

    def _handle_view_course_details(self, respect_visibility=False):
        code = self.view.get_string_input("Enter Course Code (e.g., CS101 or CS401): ").upper()
        course = self.model.get_course(code)
        if course is None:
            print(f"  [!] Error: Course '{code}' not found.")
            return
        self.view.display_course_profile(course, respect_visibility=respect_visibility)

    def _handle_view_prerequisites(self):
        code = self.view.get_string_input("Enter Course Code: ").upper()
        course = self.model.get_course(code)
        if course is None:
            print(f"  [!] Error: Course '{code}' not found.")
            return
        prereqs = self.model.get_prerequisites_for_course(code)
        self.view.display_prerequisites(course, prereqs)

    def _handle_view_unlocked_courses(self):
        code = self.view.get_string_input("Enter Course Code: ").upper()
        course = self.model.get_course(code)
        if course is None:
            print(f"  [!] Error: Course '{code}' not found.")
            return
        unlocked = self.model.get_courses_unlocked_by(code)
        self.view.display_unlocked_courses(course, unlocked)

    def _handle_add_course_on_demand(self):
        print("\n--- Add New Course On-Demand (New Vertex) ---")
        if len(self.model.get_all_courses()) >= self.model.MAX_COURSES:
            print(f"  [!] Limit Reached: System already contains the maximum of {self.model.MAX_COURSES} courses.")
            return

        code = self.view.get_string_input("Enter New Course Code (e.g., CS403): ").upper()
        if self.model.get_course(code) is not None:
            print(f"  [!] Duplicate Error: Course '{code}' already exists.")
            return

        name = self.view.get_string_input("Enter Course Name: ")
        credits = self.view.get_int_input("Enter Credit Hours (1-6): ", min_val=1, max_val=6)
        level = self.view.get_level_input("Enter Course Level ('Core' or 'Elective'): ")
        semester = self.view.get_int_input("Enter Target Semester (1-8): ", min_val=1, max_val=8)

        new_course = Course(code, name, credits, level, semester)
        success, message = self.model.add_course(new_course)
        print(f"\n  {message}")

    def _handle_add_prerequisite_on_demand(self):
        print("\n--- Add Prerequisite On-Demand (Create Incoming Edge Y -> X) ---")
        target_x = self.view.get_string_input("Enter Target Course X (course that requires the prerequisite): ").upper()
        if self.model.get_course(target_x) is None:
            print(f"  [!] Error: Target course '{target_x}' does not exist.")
            return

        prereq_y = self.view.get_string_input(f"Enter Prerequisite Course Y (to be required by {target_x}): ").upper()
        success, message = self.model.add_prerequisite(target_x, prereq_y)
        print(f"\n  {message}")

    def _handle_remove_prerequisite_on_demand(self):
        print("\n--- Remove Prerequisite On-Demand (Remove Edge Y -> X) ---")
        target_x = self.view.get_string_input("Enter Target Course X: ").upper()
        if self.model.get_course(target_x) is None:
            print(f"  [!] Error: Target course '{target_x}' does not exist.")
            return

        prereq_y = self.view.get_string_input(f"Enter Prerequisite Course Y to remove from {target_x}: ").upper()
        success, message = self.model.remove_prerequisite(target_x, prereq_y)
        print(f"\n  {message}")


if __name__ == "__main__":
    app = CourseController()
    app.run()