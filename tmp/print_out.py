import requests

salary_json = """{
  "mapping": {
    "name": "Employee_Salary_Calculation",
    "source": {
      "type": "database",
      "fields": {
        "employee_id": 101,
        "salary": 50000,
        "bonus": 5000
      }
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
        "source_code": salary_json,
        "from_lang": "iics",
        "to_lang": "ktr",
        "file_name": "Employee_Salary_Calculation.json",
    }
)

d = res.json()
print("=== LEFT TERMINAL (SOURCE STDOUT) ===")
print(d.get("source_output"))
print("\n=== RIGHT TERMINAL (TARGET STDOUT) ===")
print(d.get("target_output"))
