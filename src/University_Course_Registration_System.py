"""
Title: University Course Registration System – Metrics-Based Refactoring

Project Description:
The following Python code implements a University Course Registration System, but the design 
has several issues that violate good software engineering principles.

Tasks:
- Analyze the code using software metrics (CK metrics, Cyclomatic Complexity, LOC, cohesion, coupling)
- Identify problematic areas based on metric results
- Refactor the code to improve maintainability and design quality
"""

from datetime import datetime


class Person:
    def __init__(self, person_id, name, email, phone=None):
        self.person_id = person_id
        self.name = name
        self.email = email
        self.phone = phone
        self.role = None

    def display_info(self):
        print(f"ID: {self.person_id}, Name: {self.name}, Email: {self.email}, Phone: {self.phone}")

    def update_contact(self, email, phone):
        self.email = email
        self.phone = phone
        print(f"{self.name}'s contact updated.")

 
class Student(Person):
    def __init__(self, student_id, name, email, phone=None):
        super().__init__(student_id, name, email, phone)
        self.role = "Student"
        self.courses = []
        self.grades = {}
        self.attendance = {}
        self.last_login = datetime.now()

    def register_course(self, course):
        """Register student for a course (public API).
        This method ensures student's course list is updated and
        encapsulates any future validation.
        """
        if course.code not in [c.code for c in self.courses]:
            self.courses.append(course)
            return True
        return False

    def add_grade(self, course_code, grade):
        """Encapsulated API to add/replace a grade for the student."""
        self.grades[course_code] = grade

    def add_attendance(self, course_code, records):
        """Encapsulated API to set attendance records for a course."""
        self.attendance[course_code] = records


    # calculate_performance removed. Performance is handled by
    # PerformanceCalculator for better separation of concerns.


class Course:
    def __init__(self, code, title, credit_hours, lecturer=None):
        self.code = code
        self.title = title
        self.credit_hours = credit_hours
        self.lecturer = lecturer
        self.students = []

    def enroll_student(self, student):
        # Only update the course's enrollment list here. Student-side
        # registration is done by Registrar.enroll to reduce bidirectional
        # coupling and centralize coordination.
        if student not in self.students:
            self.students.append(student)
            return True
        return False

    def display_details(self):
        print(f"{self.code}: {self.title}, Credits: {self.credit_hours}, Lecturer: {self.lecturer.name if self.lecturer else 'TBA'}")
        print("Enrolled students:")
        for s in self.students:
            print(f"- {s.name}")


class Lecturer(Person):
    def __init__(self, staff_id, name, email, department):
        super().__init__(staff_id, name, email)
        self.role = "Lecturer"
        self.department = department
        self.courses = []

    def assign_course(self, course):
        if course not in self.courses:
            self.courses.append(course)
            course.lecturer = self
            print(f"{self.name} assigned to {course.title}")

    def submit_grades(self, students, course_code, grade):
        """Submit grades via Student API rather than direct attribute access."""
        for s in students:
            s.add_grade(course_code, grade)
        # Reporting/logging left to higher level (Registrar/ReportGenerator)

    def print_summary(self):
        print(f"Lecturer: {self.name}")
        for c in self.courses:
            print(f"Teaching: {c.title} ({len(c.students)} students)")


class Registrar:
    def __init__(self):
        self.students = []
        self.courses = []
        self.lecturers = []

    def add_student(self, s):
        self.students.append(s)
        print(f"Added student {s.name}")

    def add_course(self, c):
        self.courses.append(c)

    def add_lecturer(self, l):
        self.lecturers.append(l)

    def enroll(self, student, course):
        """Centralized enrollment: update both course and student records."""
        added_to_course = course.enroll_student(student)
        added_to_student = student.register_course(course)
        if added_to_course and added_to_student:
            print(f"{student.name} enrolled in {course.title}")
            return True
        # If either side already had the relation, keep consistent state
        return False

    def generate_report(self):
        """Create a full report using a dedicated ReportGenerator."""
        rg = ReportGenerator(self)
        rg.print_full_report()
        

class PerformanceCalculator:
    """Service responsible for performance calculations (GPA and attendance).

    This separates numeric logic from Student presentation and reduces
    cyclomatic complexity in domain objects.
    """
    GRADE_POINTS = {
        'A': 4,
        'B': 3,
        'C': 2,
        'D': 1,
        'E': 0,
    }

    @classmethod
    def calculate_gpa(cls, grades):
        if not grades:
            return 0.0
        total = 0
        for grade in grades.values():
            total += cls.GRADE_POINTS.get(grade, 0)
        return round(total / len(grades), 2)

    @classmethod
    def average_attendance(cls, attendance):
        if not attendance:
            return 0.0
        total_pct = 0.0
        for records in attendance.values():
            if not records:
                continue
            attended = sum(1 for r in records if r)
            total_pct += (attended / len(records)) * 100
        return total_pct / len(attendance) if attendance else 0.0


class ReportGenerator:
    """Handles presentation of reports for Registrar, Lecturer and Course."""
    def __init__(self, registrar: 'Registrar'):
        self.registrar = registrar

    def print_full_report(self):
        print("=== Full University Report ===")
        for c in self.registrar.courses:
            c.display_details()
        for l in self.registrar.lecturers:
            l.print_summary()
        for s in self.registrar.students:
            gpa = PerformanceCalculator.calculate_gpa(s.grades)
            att = PerformanceCalculator.average_attendance(s.attendance)
            print(f"Student: {s.name} - GPA: {gpa}, Attendance: {att:.1f}%")
            if gpa >= 3.5 and att >= 90:
                print("Excellent performance!")
            elif gpa < 2.0 or att < 60:
                print("Warning: Poor performance")


def main():
    reg = Registrar()

    c1 = Course("CS101", "Intro to Programming", 3)
    c2 = Course("CS201", "Data Structures", 4)

    l1 = Lecturer("L001", "Dr. Smith", "smith@uni.com", "CS")
    reg.add_lecturer(l1)

    s1 = Student("S001", "Alice", "alice@uni.com")
    s2 = Student("S002", "Bob", "bob@uni.com")
    reg.add_student(s1)
    reg.add_student(s2)

    l1.assign_course(c1)
    c1.enroll_student(s1)
    c1.enroll_student(s2)
    l1.submit_grades([s1, s2], "CS101", "A")

    s1.attendance["CS101"] = [True, True, False, True]
    s2.attendance["CS101"] = [True, False, True, False]

    reg.add_course(c1)
    reg.add_course(c2)
    reg.full_report()

if __name__ == "__main__":
    main()
