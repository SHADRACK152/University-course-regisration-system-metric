# University Course Registration System — Final Report

**Group Members:**
- Trevor Maosa — INTE/MG/2907/09/22
- Deborah Anyango — INTE/MG/2889/09/22
- Shadrack Mark Emadau — INTE/MG/278709/22

**GitHub repository:** https://github.com/SHADRACK152/University-course-regisration-system-metric

---

**Overview**

This report summarizes the metrics-based analysis and refactoring of the `University_Course_Registration_System.py` code. The deliverables include:
- Part A: Metrics analysis (original)
- Part B: Diagnosis of design issues
- Part C: Refactoring and post-refactor metrics

Files used/generated in this workspace:
- `src/University_Course_Registration_System.py` — refactored implementation
- `src/metrics_analyzer.py` — AST-based analyzer used to compute CBO/DIT/LCOM-like metrics
- `reports/metrics_analysis_original.txt` — original metrics (pre-refactor)
- `reports/metrics_analysis_refactored.txt` — post-refactor metrics from the analyzer
- `reports/part_b_diagnosis.txt` — diagnosis (Part B)
- `reports/final_report.md` — this file

---

**Part A: Before (Original) — Key metrics**
(Extracted from `reports/metrics_analysis_original.txt` and tool runs)

- Total LOC (original): 174
- Average cyclomatic complexity (original): A (≈2.6)
- Hotspot: `Student.calculate_performance()` — CC = 17 (grade C)
- Maintainability Index (original): 45.34 (radon MI)
- Problems flagged: high CC in `calculate_performance`, low comments (0%), bidirectional coupling between `Course` and `Student`, direct grade mutation by `Lecturer`.

Reference (original radon/lizard outputs saved in `reports/metrics_analysis_original.txt`).

---

**Part C: After (Refactored) — Key metrics and comparison**

Post-refactor measures (computed on `src/University_Course_Registration_System.py` after refactor):

- Total LOC (refactored): 231 (increase due to new small services and reporting classes)
- Average cyclomatic complexity (refactored): A (≈2.31)
- Maintainability Index (refactored): 49.53 (radon MI)
- No functions exceed CC > 15 after refactor (previous hotspot removed)

Before / After comparison (high level):

- `Student.calculate_performance()` — CC: 17 → removed (logic moved to `PerformanceCalculator`)
- Average CC (file): A (≈2.62) → A (≈2.31)
- LOC: 174 → 231 (added classes but reduced complexity in single methods)
- MI: 45.34 → 49.53 (improved)
- Functions with CC > 10: 1 (original) → 0 (refactored)

Detailed per-method CC (highlights):
- Before: `Student.calculate_performance` CC=17
- After: `PerformanceCalculator.average_attendance` CC=7, `ReportGenerator.print_full_report` CC=8, both well under the problem threshold.

Files with analyzer results saved to `reports/metrics_analysis_refactored.txt` and radon outputs available in the repo.

---

**What changed (refactor summary)**

- Extracted performance calculation into a dedicated `PerformanceCalculator` class with:
  - `calculate_gpa(grades)`
  - `average_attendance(attendance)`
  This reduced logical branching inside `Student` and made the algorithms easier to test.

- Removed `Student.calculate_performance()` and added small, focused APIs on `Student`:
  - `add_grade(course_code, grade)`
  - `add_attendance(course_code, records)`
  - `register_course(course)` now returns success status instead of printing.

- Reduced bidirectional coupling by centralizing enrollment in `Registrar.enroll(student, course)` instead of `Course.enroll_student` calling `student.register_course` directly.

- Changed `Lecturer.submit_grades` to use `Student.add_grade(...)` rather than mutating `s.grades` directly (improved encapsulation).

- Moved reporting to a `ReportGenerator` service which uses `PerformanceCalculator` to compute and present metrics, separating presentation from business logic.

- Added small unit-friendly APIs and removed direct print-based logic from domain methods where possible.

**Selected before/after code snippets**

Before (original `Student.calculate_performance` simplified):

```py
# original (high CC)
for code, grade in self.grades.items():
    if grade == "A": total_points += 4
    elif grade == "B": total_points += 3
    # ...
# Attendance aggregation and printing inside same method
```

After (extracted into `PerformanceCalculator`):

```py
class PerformanceCalculator:
    GRADE_POINTS = {'A':4,'B':3,'C':2,'D':1,'E':0}
    @classmethod
    def calculate_gpa(cls, grades):
        if not grades: return 0.0
        total = sum(cls.GRADE_POINTS.get(g,0) for g in grades.values())
        return round(total / len(grades), 2)

    @classmethod
    def average_attendance(cls, attendance):
        if not attendance: return 0.0
        # compute percent per-course then average
```

**Why this improves design (short)**
- Lower cyclomatic complexity inside objects — easier to test and reason about.
- Better cohesion: each class has a focused responsibility.
- Reduced coupling: `Registrar` coordinates interactions; domain objects expose small, testable APIs.
- Improved encapsulation: `Student` controls how grades/attendance are stored.

---

**Where to find artifacts**
- `reports/metrics_analysis_original.txt` — original analyzer output
- `reports/metrics_analysis_refactored.txt` — post-refactor analyzer output
- `reports/part_b_diagnosis.txt` — diagnosis and refactor priorities
- `src/University_Course_Registration_System.py` — refactored code
- GitHub: https://github.com/SHADRACK152/University-course-regisration-system-metric

---

**How to export this report to PDF (recommended)**

Option A — Browser (HTML):
1. Convert `final_report.md` to HTML using any Markdown viewer or open it in VS Code and use a Markdown preview.
2. Print the preview and choose "Save as PDF".

Option B — pandoc (if available locally):
```bash
pandoc reports/final_report.md -o reports/final_report.pdf
```

(You requested no environment dependency changes; I did not add any new packages to the project.)

---

**Suggested next steps**
- I can update `main()` to use the new `Registrar.enroll` and `Registrar.generate_report` APIs and run the script to confirm runtime behavior.
- I can prepare a short test script showing unit tests for `PerformanceCalculator.calculate_gpa` and `average_attendance`.
- I can produce a ready-to-export HTML version of this report for easy PDF printing.

Tell me which you prefer and I'll proceed.
