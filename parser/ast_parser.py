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
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)

        analyzer = CodeAnalyzer()
        analyzer.visit(tree)

        return {
            "file": file_path,
            "classes": analyzer.classes,
            "functions": analyzer.functions,
            "imports": analyzer.imports,
            "error": None
        }
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}")
        return {
            "file": file_path,
            "classes": [],
            "functions": [],
            "imports": [],
            "error": f"Syntax error: {e}"
        }
    except UnicodeDecodeError:
        print(f"⚠️  Encoding error in {file_path}")
        return {
            "file": file_path,
            "classes": [],
            "functions": [],
            "imports": [],
            "error": "Encoding error"
        }
    except Exception as e:
        print(f"⚠️  Error analyzing {file_path}: {e}")
        return {
            "file": file_path,
            "classes": [],
            "functions": [],
            "imports": [],
            "error": str(e)
        }


def analyze_directory(directory):
    results = []
    error_count = 0
    success_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                result = analyze_file(path)
                results.append(result)
                
                if result.get("error"):
                    error_count += 1
                else:
                    success_count += 1

    print(f"✅ Successfully analyzed {success_count} files")
    if error_count > 0:
        print(f"⚠️  Skipped {error_count} files due to errors")

    return results


if __name__ == "__main__":
    output = analyze_directory("sample_project")
    print("FILES FOUND:", len(output))
    print(json.dumps(output, indent=4))