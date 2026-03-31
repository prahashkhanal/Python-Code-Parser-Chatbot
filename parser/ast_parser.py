import ast
import os
import json


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []

        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node):
        class_info = {
            "class_name": node.name,
            "methods": []
        }

        self.current_class = class_info
        self.classes.append(class_info)

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        function_info = {
            "function_name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "calls": []
        }

        self.current_function = function_info

        if self.current_class:
            self.current_class["methods"].append(function_info)
        else:
            self.functions.append(function_info)

        self.generic_visit(node)
        self.current_function = None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")

    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.current_function["calls"].append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.current_function["calls"].append(
                    f"{ast.unparse(node.func)}"
                )

        self.generic_visit(node)


def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    return {
        "file": file_path,
        "classes": analyzer.classes,
        "functions": analyzer.functions,
        "imports": analyzer.imports,
    }


def analyze_directory(directory):
    results = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                results.append(analyze_file(path))

    return results


if __name__ == "__main__":
    output = analyze_directory("sample_project")
    print("FILES FOUND:", len(output))
    print(json.dumps(output, indent=4))