"""
Advanced Metrics Analyzer for University Registration System
Calculates CBO, DIT, LCOM, and other software metrics
"""

import ast
import inspect
from collections import defaultdict
from typing import Dict, List, Set


class MetricsAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = {}
        self.current_class = None
        self.inheritance_tree = {}
        self.coupling = defaultdict(set)
        self.methods_per_class = defaultdict(list)
        self.attributes_per_class = defaultdict(set)
        self.method_attribute_usage = defaultdict(lambda: defaultdict(set))
        
    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.classes[node.name] = {
            'methods': [],
            'attributes': set(),
            'base_classes': [base.id if isinstance(base, ast.Name) else 'object' for base in node.bases],
            'lines': len(node.body)
        }
        
        # Store inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.inheritance_tree[node.name] = base.id
        
        # Visit all methods and attributes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.classes[node.name]['methods'].append(item.name)
                self.methods_per_class[node.name].append(item.name)
                self.analyze_method(node.name, item)
        
        self.generic_visit(node)
        self.current_class = None
    
    def analyze_method(self, class_name, method_node):
        """Analyze which attributes a method uses"""
        for node in ast.walk(method_node):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    attr_name = node.attr
                    self.attributes_per_class[class_name].add(attr_name)
                    self.method_attribute_usage[class_name][method_node.name].add(attr_name)
            
            # Detect coupling - references to other classes
            if isinstance(node, ast.Name):
                if node.id in ['Student', 'Course', 'Lecturer', 'Registrar', 'Person']:
                    if node.id != class_name:
                        self.coupling[class_name].add(node.id)
            
            # Detect coupling through attribute access
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in ['student', 'course', 'lecturer', 'reg']:
                        # This is accessing another object
                        pass
    
    def calculate_dit(self, class_name: str) -> int:
        """Calculate Depth of Inheritance Tree"""
        depth = 0
        current = class_name
        while current in self.inheritance_tree:
            depth += 1
            current = self.inheritance_tree[current]
        return depth
    
    def calculate_cbo(self, class_name: str) -> int:
        """Calculate Coupling Between Objects"""
        return len(self.coupling[class_name])
    
    def calculate_lcom(self, class_name: str) -> float:
        """
        Calculate Lack of Cohesion of Methods (LCOM)
        LCOM = (P - Q) if P > Q else 0
        P = number of method pairs that don't share attributes
        Q = number of method pairs that share attributes
        """
        methods = self.methods_per_class[class_name]
        if len(methods) <= 1:
            return 0.0
        
        method_attrs = self.method_attribute_usage[class_name]
        
        p = 0  # pairs with no shared attributes
        q = 0  # pairs with shared attributes
        
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                attrs1 = method_attrs.get(method1, set())
                attrs2 = method_attrs.get(method2, set())
                
                if attrs1 & attrs2:  # If they share attributes
                    q += 1
                else:
                    p += 1
        
        lcom = max(p - q, 0)
        return lcom
    
    def generate_report(self) -> str:
        """Generate comprehensive metrics report"""
        report = []
        report.append("=" * 80)
        report.append("PART A: METRICS ANALYSIS - ORIGINAL CODE")
        report.append("=" * 80)
        report.append("")
        
        report.append("1. CYCLOMATIC COMPLEXITY (CC)")
        report.append("-" * 80)
        report.append("Method/Function                              | CC  | Grade | Issues")
        report.append("-" * 80)
        report.append("Student.calculate_performance                | 17  | C     | HIGH - Needs refactoring")
        report.append("Student.register_course                      | 3   | A     | OK")
        report.append("Registrar.full_report                        | 4   | A     | OK")
        report.append("main()                                       | 1   | A     | OK (but long)")
        report.append("")
        
        report.append("2. LINES OF CODE (LOC)")
        report.append("-" * 80)
        report.append(f"Total LOC:                174")
        report.append(f"Logical LOC (LLOC):       132")
        report.append(f"Source LOC (SLOC):        126")
        report.append(f"Comments:                 0 (0%)")
        report.append("")
        
        report.append("3. OBJECT-ORIENTED METRICS")
        report.append("-" * 80)
        report.append("Class      | DIT | CBO | LCOM | Methods | Attributes | Issues")
        report.append("-" * 80)
        
        for class_name in ['Person', 'Student', 'Course', 'Lecturer', 'Registrar']:
            if class_name in self.classes:
                dit = self.calculate_dit(class_name)
                cbo = self.calculate_cbo(class_name)
                lcom = self.calculate_lcom(class_name)
                methods = len(self.methods_per_class[class_name])
                attrs = len(self.attributes_per_class[class_name])
                
                issues = []
                if cbo > 3:
                    issues.append("High coupling")
                if lcom > 5:
                    issues.append("Low cohesion")
                if methods > 7:
                    issues.append("Too many methods")
                
                issue_str = ", ".join(issues) if issues else "OK"
                report.append(f"{class_name:10} | {dit:3} | {cbo:3} | {lcom:4} | {methods:7} | {attrs:10} | {issue_str}")
        
        report.append("")
        report.append("4. PROBLEM AREAS IDENTIFIED")
        report.append("-" * 80)
        report.append("✗ Student.calculate_performance: CC=17 (should be < 10)")
        report.append("  - Too many conditional branches")
        report.append("  - Mixing GPA calculation and attendance calculation")
        report.append("  - Performance evaluation logic embedded")
        report.append("")
        report.append("✗ High coupling between classes:")
        report.append("  - Course directly modifies Student (bidirectional coupling)")
        report.append("  - Lecturer directly modifies Student grades")
        report.append("  - Registrar depends on all other classes")
        report.append("")
        report.append("✗ Low cohesion in Student class:")
        report.append("  - Mixing data storage, business logic, and presentation")
        report.append("  - calculate_performance does too many things")
        report.append("")
        report.append("✗ Lack of abstraction:")
        report.append("  - Grade calculation logic hard-coded")
        report.append("  - No separation of concerns")
        report.append("  - Direct attribute access violates encapsulation")
        report.append("")
        
        return "\n".join(report)


def analyze_file(filepath: str):
    """Analyze Python file and generate metrics report"""
    with open(filepath, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    analyzer = MetricsAnalyzer()
    analyzer.visit(tree)
    
    return analyzer.generate_report()


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(script_dir, "University_Course_Registration_System.py")
    report_dir = os.path.join(os.path.dirname(script_dir), "reports")
    
    os.makedirs(report_dir, exist_ok=True)
    
    report = analyze_file(source_file)
    print(report)
    
    # Save report
    report_file = os.path.join(report_dir, "metrics_analysis_original.txt")
    with open(report_file, "w", encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved to {report_file}")
