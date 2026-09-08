import requests

filter_json = """{
  "mapping": {
    "name": "Employee_Filter_Calculation",
    "source": {
      "type": "database",
      "fields": {
        "employee_id": 101,
        "salary": 50000,
        "bonus": 5000
      }
    },
    "filter": {
      "type": "filter",
      "condition": "salary <= 2000"
    },
    "transformation": {
      "type": "expression",
      "logic": {
        "total_salary": "salary + bonus"
      }
    },
    "target": {
      "type": "output",
      "fields": {
        "employee_id": 101,
        "total_salary": 55000
      }
    }
  }
}"""

res = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": filter_json,
        "from_lang": "iics",
        "to_lang": "ktr",
        "file_name": "Employee_Filter_Calculation.json",
    }
)

d = res.json()
with open("tmp/filter_out.txt", "w") as f:
    f.write("=== LEFT TERMINAL (SOURCE STDOUT) ===\n")
    f.write(str(d.get("source_output")))
    f.write("\n\n=== RIGHT TERMINAL (TARGET STDOUT) ===\n")
    f.write(str(d.get("target_output")))
    f.write("\n\n=== GENERATED KTR XML ===\n")
    f.write(str(d.get("converted_code")))

print("Wrote tmp/filter_out.txt")
