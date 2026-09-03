import json

# -----------------------------
# JSON Generator Snap
# -----------------------------
def json_generator():
    return [
        {
                "id": 1,
                "name": "Alice"
        },
        {
                "id": 2,
                "name": "Bob"
        }
]

# -----------------------------
# Mapper Snap
# -----------------------------
def mapper(records):
    output = []

    for record in records:
        output.append({
            "employee_id": record["id"]
            "employee_name": record["name"]
        })

    return output

# -----------------------------
# JSON Formatter Snap
# -----------------------------
def json_formatter(records):
    return json.dumps(records, indent=4)

# -----------------------------
# Pipeline Execution
# -----------------------------
def execute_pipeline():

    print("Step 1 : JSON Generator")
    data = json_generator()
    print(data)
    print("\nStep 2 : Mapper")
    mapped_data = mapper(data)
    print(mapped_data)
    print("\nStep 3 : JSON Formatter")
    formatted_json = json_formatter(mapped_data)
    print(formatted_json)


if __name__ == "__main__":
    execute_pipeline()
