import requests
import json

user_iics_json = """{
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

large_enterprise_iics_json = """{
  "name": "Enterprise_Customer_Orders_ETL",
  "transformations": [
    {
      "name": "Extract_Orders",
      "type": "Source",
      "table": "raw_orders",
      "fields": [
        {"name": "order_id", "type": "Integer"},
        {"name": "customer_id", "type": "Integer"},
        {"name": "amount", "type": "Number"},
        {"name": "status", "type": "String"}
      ]
    },
    {
      "name": "Filter_Completed_Orders",
      "type": "Filter",
      "logic": "status = 'COMPLETED'"
    },
    {
      "name": "Compute_Tax_And_Total",
      "type": "Expression",
      "logic": [
        {"field": "tax_amount", "expr": "amount * 0.18"},
        {"field": "total_amount", "expr": "amount + tax_amount"}
      ]
    },
    {
      "name": "Load_DW_Orders",
      "type": "Target",
      "table": "dw_fact_orders",
      "fields": [
        {"name": "order_id", "type": "Integer"},
        {"name": "customer_id", "type": "Integer"},
        {"name": "total_amount", "type": "Number"}
      ]
    }
  ]
}"""

print("================= TEST 1: USER'S NUMBER_SWAP IICS JSON =================")
res1 = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": user_iics_json,
        "from_lang": "iics",
        "to_lang": "ktr",
        "file_name": "Number_Swap.json",
    }
)
d1 = res1.json()
print("STATUS:", d1.get("status"))
print("GENERATED PENTAHO KTR XML:\n")
print(d1.get("converted_code"))

print("\n================= TEST 2: LARGE ENTERPRISE ETL IICS JSON =================")
res2 = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": large_enterprise_iics_json,
        "from_lang": "iics",
        "to_lang": "ktr",
        "file_name": "Enterprise_Customer_Orders_ETL.json",
    }
)
d2 = res2.json()
print("STATUS:", d2.get("status"))
print("GENERATED PENTAHO KTR XML:\n")
print(d2.get("converted_code"))
