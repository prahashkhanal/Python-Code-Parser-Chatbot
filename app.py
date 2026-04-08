from parser.ast_parser import analyze_directory
from storage.database import create_tables, insert_file, insert_function


if __name__ == "__main__":
    create_tables()

    data = analyze_directory("sample_project")

    for file in data:
        # Skip files with parsing errors
        if file.get("error"):
            continue

        file_id = insert_file(file["file"])

        # Standalone functions
        for func in file["functions"]:
            insert_function(file_id, func["function_name"], func["calls"])

        # Class methods
        for cls in file["classes"]:
            for method in cls["methods"]:
                insert_function(file_id, method["function_name"], method["calls"])

    print("Project data stored successfully.")