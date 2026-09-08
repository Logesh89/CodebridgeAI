import requests
import json

java_code = """public class SwapNumbers {
    public static void main(String[] args) {
        float first = 1.20f, second = 2.45f;

        System.out.println("--Before swap--");
        System.out.println("First number = " + first);
        System.out.println("Second number = " + second);

        // Value of first is assigned to temporary
        float temporary = first;

        // Value of second is assigned to first
        first = second;

        // Value of temporary is assigned to second
        second = temporary;

        System.out.println("--After swap--");
        System.out.println("First number = " + first);
        System.out.println("Second number = " + second);
    }
}"""

print("================= TEST 1: JAVA TO PYTHON =================")
res1 = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": java_code,
        "from_lang": "java",
        "to_lang": "python",
        "file_name": "SwapNumbers.java",
    }
)

d1 = res1.json()
print("Conversion Status:", d1.get("status"))
print("Compilation Message:", d1.get("compilation_message"))
print("\n--- CONVERTED PYTHON CODE ---")
print(d1.get("converted_code"))
print("\n--- TARGET PYTHON EXECUTED OUTPUT ---")
print(d1.get("target_output"))
print("\n--- OUTPUT PARITY MATCH ---")
print(d1.get("output_match"))


print("\n================= TEST 2: JAVA TO C =================")
res2 = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": java_code,
        "from_lang": "java",
        "to_lang": "c",
        "file_name": "SwapNumbers.java",
    }
)

d2 = res2.json()
print("Conversion Status:", d2.get("status"))
print("Compilation Message:", d2.get("compilation_message"))
print("\n--- CONVERTED C CODE ---")
print(d2.get("converted_code"))
print("\n--- TARGET C EXECUTED OUTPUT ---")
print(d2.get("target_output"))
print("\n--- OUTPUT PARITY MATCH ---")
print(d2.get("output_match"))
