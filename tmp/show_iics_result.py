import requests

user_json = """{
  "mapping": {
    "name": "Number_Swap",
    "source": {
      "type": "input",
      "fields": {
        "first": 1.20,
        "second": 2.45
      }
    },
    "transformation": {
      "type": "expression",
      "logic": {
        "temporary": "first",
        "first": "second",
        "second": "temporary"
      }
    },
    "target": {
      "type": "output",
      "fields": {
        "first": 2.45,
        "second": 1.20
      }
    }
  }
}"""

res = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": user_json,
        "from_lang": "iics",
        "to_lang": "ktr",
        "file_name": "Number_Swap.json"
    }
)

d = res.json()
print("STATUS:", d.get("status"))
print("COMPILATION MSG:", d.get("compilation_message"))
print("\n--- GENERATED PENTAHO KTR XML ---")
print(d.get("converted_code"))
