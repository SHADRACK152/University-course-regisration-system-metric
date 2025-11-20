"""
University Course Registration System - REFACTORED VERSION
Part C: Refactored code with improved design

Improvements:
1. Reduced Cyclomatic Complexity (extracted methods, strategy pattern)
2. Reduced Coupling (dependency injection, service layer)
3. Improved Cohesion (single responsibility per class)
4. Better Encapsulation (private attributes, proper interfaces)
5. Applied SOLID principles
"""

from datetime import datetime
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


# ============================================================================
# STRATEGY PATTERN: Grade Calculation
# ============================================================================

class GradeCalculator(ABC):
    """Abstract base class for grade calculation strategies"""
    
    @abstractmethod
    def calculate_points(self, grade: str) -> float:
        """Convert letter grade to grade points"""
        pass


class StandardGradeCalculator(GradeCalculator):
    """Standard 4.0 GPA scale calculator"""
    
    def __init__(self):
        self._grade_map = {
            "A": 4.0,
            "B": 3.0,
            "C": 2.0,
            "D": 1.0,
            "E": 0.0,
            "F": 0.0
        }
    
    def calculate_points(self, grade: str) -> float:
        """Convert letter grade to points"""
        return self._grade_map.get(grade.upper(), 0.0)


# ============================================================================
# VALUE OBJECTS: Encapsulated calculations
# ============================================================================

class GPACalculator:
    """Handles GPA calculation logic - Single Responsibility"""
    
    def __init__(self, grade_calculator: GradeCalculator):
        self._grade_calculator = grade_calculator
    
    def calculate_gpa(self, grades: Dict[str, str]) -> float:
        """Calculate GPA from grades dictionary"""
        if not grades:
            return 0.0
        
        total_points = sum(
            self._grade_calculator.calculate_points(grade)
            for grade in grades.values()
        )
        return round(total_points / len(grades), 2)


class AttendanceCalculator:
    """Handles attendance calculation logic - Single Responsibility"""
    
    def calculate_average_attendance(self, attendance_records: Dict[str, List[bool]]) -> float:
        """Calculate average attendance percentage across all courses"""
        if not attendance_records:
            return 0.0
        
        course_attendance_rates = []
        for records in attendance_records.values():
            if records:
                attended = sum(1 for r in records if r)
                rate = (attended / len(records)) * 100
                course_attendance_rates.append(rate)
        
        if not course_attendance_rates:
            return 0.0
        
        return round(sum(course_attendance_rates) / len(course_attendance_rates), 1)


class PerformanceEvaluator:
    """Evaluates student performance - Single Responsibility"""
    
    def __init__(self, excellent_gpa: float = 3.5, excellent_attendance: float = 90.0,
                 poor_gpa: float = 2.0, poor_attendance: float = 60.0):
        self._excellent_gpa = excellent_gpa
        self._excellent_attendance = excellent_attendance
        self._poor_gpa = poor_gpa
        self._poor_attendance = poor_attendance
    
    def evaluate(self, gpa: float, attendance: float) -> str:
        """Evaluate performance and return status"""
        if gpa >= self._excellent_gpa and attendance >= self._excellent_attendance:
            return "Excellent performance!"
        elif gpa < self._poor_gpa or attendance < self._poor_attendance:
            return "Warning: Poor performance"
        return "Satisfactory performance"


# ============================================================================
# DOMAIN MODELS: Core entities
# ============================================================================

class Person:
    """Base class for all persons in the system"""
    
    def __init__(self, person_id: str, name: str, email: str, phone: Optional[str] = None):
        self._person_id = person_id
        self._name = name
        self._email = email
        self._phone = phone
        self._role = None
    
    @property
    def person_id(self) -> str:
        return self._person_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def phone(self) -> Optional[str]:
        return self._phone
    
    def update_contact(self, email: str, phone: str) -> None:
        """Update contact information"""
        self._email = email
        self._phone = phone
    
    def display_info(self) -> str:
        """Return formatted person information"""
        return f"ID: {self._person_id}, Name: {self._name}, Email: {self._email}, Phone: {self._phone}"


class Student(Person):
    """Student entity - focused on data storage only"""
    
    def __init__(self, student_id: str, name: str, email: str, phone: Optional[str] = None):
        super().__init__(student_id, name, email, phone)
        self._role = "Student"
        self._enrolled_courses: List[str] = []  # Store course codes only
        self._grades: Dict[str, str] = {}
        self._attendance: Dict[str, List[bool]] = {}
        self._last_login = datetime.now()
    
    def add_course(self, course_code: str) -> bool:
        """Add course to student's enrolled courses"""
        if course_code not in self._enrolled_courses:
            self._enrolled_courses.append(course_code)
            return True
        return False
    
    def is_enrolled(self, course_code: str) -> bool:
        """Check if student is enrolled in course"""
        return course_code in self._enrolled_courses
    
    def add_grade(self, course_code: str, grade: str) -> None:
        """Add grade for a course"""
        self._grades[course_code] = grade
    
    def add_attendance_record(self, course_code: str, attended: bool) -> None:
        """Add attendance record for a course"""
        if course_code not in self._attendance:
            self._attendance[course_code] = []
        self._attendance[course_code].append(attended)
    
    def get_grades(self) -> Dict[str, str]:
        """Get all grades"""
        return self._grades.copy()
    
    def get_attendance(self) -> Dict[str, List[bool]]:
        """Get all attendance records"""
        return self._attendance.copy()
    
    def get_enrolled_courses(self) -> List[str]:
        """Get list of enrolled course codes"""
        return self._enrolled_courses.copy()


class Course:
    """Course entity - focused on course information"""
    
    def __init__(self, code: str, title: str, credit_hours: int, lecturer_id: Optional[str] = None):
        self._code = code
        self._title = title
        self._credit_hours = credit_hours
        self._lecturer_id = lecturer_id
        self._enrolled_students: List[str] = []  # Store student IDs only
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def credit_hours(self) -> int:
        return self._credit_hours
    
    @property
    def lecturer_id(self) -> Optional[str]:
        return self._lecturer_id
    
    def set_lecturer(self, lecturer_id: str) -> None:
        """Assign lecturer to course"""
        self._lecturer_id = lecturer_id
    
    def add_student(self, student_id: str) -> bool:
        """Add student to course"""
        if student_id not in self._enrolled_students:
            self._enrolled_students.append(student_id)
            return True
        return False
    
    def get_enrolled_students(self) -> List[str]:
        """Get list of enrolled student IDs"""
        return self._enrolled_students.copy()
    
    def get_enrollment_count(self) -> int:
        """Get number of enrolled students"""
        return len(self._enrolled_students)


class Lecturer(Person):
    """Lecturer entity"""
    
    def __init__(self, staff_id: str, name: str, email: str, department: str):
        super().__init__(staff_id, name, email)
        self._role = "Lecturer"
        self._department = department
        self._assigned_courses: List[str] = []  # Store course codes only
    
    @property
    def department(self) -> str:
        return self._department
    
    def add_course(self, course_code: str) -> bool:
        """Add course to lecturer's assignments"""
        if course_code not in self._assigned_courses:
            self._assigned_courses.append(course_code)
            return True
        return False
    
    def get_assigned_courses(self) -> List[str]:
        """Get list of assigned course codes"""
        return self._assigned_courses.copy()


# ============================================================================
# SERVICE LAYER: Business logic and coordination
# ============================================================================

class EnrollmentService:
    """Handles enrollment operations - reduces coupling between Student and Course"""
    
    def enroll_student(self, student: Student, course: Course) -> bool:
        """Enroll student in course"""
        if student.is_enrolled(course.code):
            return False
        
        # Update both entities
        student.add_course(course.code)
        course.add_student(student.person_id)
        return True


class GradeService:
    """Handles grade operations - encapsulates grade management"""
    
    def submit_grade(self, student: Student, course_code: str, grade: str) -> None:
        """Submit grade for student in course"""
        if not student.is_enrolled(course_code):
            raise ValueError(f"Student {student.name} not enrolled in course {course_code}")
        student.add_grade(course_code, grade)


class PerformanceService:
    """Handles performance calculation and evaluation"""
    
    def __init__(self):
        self._gpa_calculator = GPACalculator(StandardGradeCalculator())
        self._attendance_calculator = AttendanceCalculator()
        self._evaluator = PerformanceEvaluator()
    
    def calculate_performance(self, student: Student) -> Dict[str, any]:
        """Calculate student performance metrics - Reduced complexity!"""
        gpa = self._gpa_calculator.calculate_gpa(student.get_grades())
        attendance = self._attendance_calculator.calculate_average_attendance(
            student.get_attendance()
        )
        evaluation = self._evaluator.evaluate(gpa, attendance)
        
        return {
            'gpa': gpa,
            'attendance': attendance,
            'evaluation': evaluation
        }


class CourseAssignmentService:
    """Handles lecturer-course assignments"""
    
    def assign_lecturer(self, lecturer: Lecturer, course: Course) -> bool:
        """Assign lecturer to course"""
        if course.code in lecturer.get_assigned_courses():
            return False
        
        lecturer.add_course(course.code)
        course.set_lecturer(lecturer.person_id)
        return True


# ============================================================================
# REPOSITORY PATTERN: Data management
# ============================================================================

class Repository:
    """Generic repository for entity storage"""
    
    def __init__(self):
        self._entities: Dict[str, any] = {}
    
    def add(self, entity_id: str, entity: any) -> None:
        """Add entity to repository"""
        self._entities[entity_id] = entity
    
    def get(self, entity_id: str) -> Optional[any]:
        """Get entity by ID"""
        return self._entities.get(entity_id)
    
    def get_all(self) -> List[any]:
        """Get all entities"""
        return list(self._entities.values())
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return entity_id in self._entities


# ============================================================================
# PRESENTATION LAYER: Output formatting
# ============================================================================

class ReportGenerator:
    """Generates reports - Separated presentation from business logic"""
    
    def __init__(self, student_repo: Repository, course_repo: Repository, 
                 lecturer_repo: Repository, performance_service: PerformanceService):
        self._student_repo = student_repo
        self._course_repo = course_repo
        self._lecturer_repo = lecturer_repo
        self._performance_service = performance_service
    
    def generate_course_report(self, course: Course) -> str:
        """Generate report for a single course"""
        lecturer = self._lecturer_repo.get(course.lecturer_id) if course.lecturer_id else None
        lecturer_name = lecturer.name if lecturer else "TBA"
        
        lines = [
            f"{course.code}: {course.title}, Credits: {course.credit_hours}, Lecturer: {lecturer_name}",
            "Enrolled students:"
        ]
        
        for student_id in course.get_enrolled_students():
            student = self._student_repo.get(student_id)
            if student:
                lines.append(f"- {student.name}")
        
        return "\n".join(lines)
    
    def generate_lecturer_report(self, lecturer: Lecturer) -> str:
        """Generate report for a lecturer"""
        lines = [f"Lecturer: {lecturer.name}"]
        
        for course_code in lecturer.get_assigned_courses():
            course = self._course_repo.get(course_code)
            if course:
                lines.append(f"Teaching: {course.title} ({course.get_enrollment_count()} students)")
        
        return "\n".join(lines)
    
    def generate_student_performance_report(self, student: Student) -> str:
        """Generate performance report for student"""
        performance = self._performance_service.calculate_performance(student)
        return (f"Student: {student.name}\n"
                f"GPA: {performance['gpa']}, "
                f"Attendance: {performance['attendance']:.1f}%\n"
                f"{performance['evaluation']}")
    
    def generate_full_report(self) -> str:
        """Generate comprehensive university report - Reduced complexity!"""
        lines = ["=" * 50, "Full University Report", "=" * 50, ""]
        
        # Course reports
        lines.append("COURSES:")
        lines.append("-" * 50)
        for course in self._course_repo.get_all():
            lines.append(self.generate_course_report(course))
            lines.append("")
        
        # Lecturer reports
        lines.append("LECTURERS:")
        lines.append("-" * 50)
        for lecturer in self._lecturer_repo.get_all():
            lines.append(self.generate_lecturer_report(lecturer))
            lines.append("")
        
        # Student performance reports
        lines.append("STUDENT PERFORMANCE:")
        lines.append("-" * 50)
        for student in self._student_repo.get_all():
            lines.append(self.generate_student_performance_report(student))
            lines.append("")
        
        return "\n".join(lines)


# ============================================================================
# FACADE PATTERN: Simplified interface
# ============================================================================

class UniversityRegistrationSystem:
    """Facade providing simplified interface to the system"""
    
    def __init__(self):
        # Repositories
        self._student_repo = Repository()
        self._course_repo = Repository()
        self._lecturer_repo = Repository()
        
        # Services
        self._enrollment_service = EnrollmentService()
        self._grade_service = GradeService()
        self._performance_service = PerformanceService()
        self._assignment_service = CourseAssignmentService()
        
        # Presentation
        self._report_generator = ReportGenerator(
            self._student_repo, self._course_repo, 
            self._lecturer_repo, self._performance_service
        )
    
    def add_student(self, student: Student) -> None:
        """Add student to system"""
        self._student_repo.add(student.person_id, student)
    
    def add_course(self, course: Course) -> None:
        """Add course to system"""
        self._course_repo.add(course.code, course)
    
    def add_lecturer(self, lecturer: Lecturer) -> None:
        """Add lecturer to system"""
        self._lecturer_repo.add(lecturer.person_id, lecturer)
    
    def enroll_student_in_course(self, student_id: str, course_code: str) -> bool:
        """Enroll student in course"""
        student = self._student_repo.get(student_id)
        course = self._course_repo.get(course_code)
        
        if not student or not course:
            return False
        
        return self._enrollment_service.enroll_student(student, course)
    
    def assign_lecturer_to_course(self, lecturer_id: str, course_code: str) -> bool:
        """Assign lecturer to course"""
        lecturer = self._lecturer_repo.get(lecturer_id)
        course = self._course_repo.get(course_code)
        
        if not lecturer or not course:
            return False
        
        return self._assignment_service.assign_lecturer(lecturer, course)
    
    def submit_grades(self, lecturer_id: str, course_code: str, 
                     student_grades: Dict[str, str]) -> None:
        """Submit grades for multiple students"""
        for student_id, grade in student_grades.items():
            student = self._student_repo.get(student_id)
            if student:
                self._grade_service.submit_grade(student, course_code, grade)
    
    def print_full_report(self) -> None:
        """Print comprehensive report"""
        print(self._report_generator.generate_full_report())


# ============================================================================
# MAIN FUNCTION: Demonstration
# ============================================================================

def main():
    """Demonstrate the refactored system - Simplified and cleaner"""
    # Initialize system
    system = UniversityRegistrationSystem()
    
    # Create courses
    c1 = Course("CS101", "Intro to Programming", 3)
    c2 = Course("CS201", "Data Structures", 4)
    system.add_course(c1)
    system.add_course(c2)
    
    # Create lecturer
    l1 = Lecturer("L001", "Dr. Smith", "smith@uni.com", "CS")
    system.add_lecturer(l1)
    
    # Create students
    s1 = Student("S001", "Alice", "alice@uni.com")
    s2 = Student("S002", "Bob", "bob@uni.com")
    system.add_student(s1)
    system.add_student(s2)
    
    # Assign lecturer to course
    system.assign_lecturer_to_course("L001", "CS101")
    
    # Enroll students
    system.enroll_student_in_course("S001", "CS101")
    system.enroll_student_in_course("S002", "CS101")
    
    # Submit grades
    system.submit_grades("L001", "CS101", {"S001": "A", "S002": "A"})
    
    # Add attendance
    s1.add_attendance_record("CS101", True)
    s1.add_attendance_record("CS101", True)
    s1.add_attendance_record("CS101", False)
    s1.add_attendance_record("CS101", True)
    
    s2.add_attendance_record("CS101", True)
    s2.add_attendance_record("CS101", False)
    s2.add_attendance_record("CS101", True)
    s2.add_attendance_record("CS101", False)
    
    # Generate report
    system.print_full_report()


if __name__ == "__main__":
    main()
