import requests
import json

java_code = """public class AsciiValue {
    public static void main(String[] args) {
        char ch = 'a';
        int ascii = ch;
        // You can also cast char to int
        int castAscii = (int) ch;

        System.out.println("The ASCII value of " + ch + " is: " + ascii);
        System.out.println("The ASCII value of " + ch + " is: " + castAscii);
    }
}"""

res = requests.post(
    "http://localhost:8005/api/v1/interpreter/convert",
    json={
        "source_code": java_code,
        "from_lang": "java",
        "to_lang": "python",
        "file_name": "AsciiValue.java",
    }
)

print("API Response Status Code:", res.status_code)
data = res.json()
print("Conversion Status:", data.get("status"))
print("Compilation Message:", data.get("compilation_message"))
print("Model Used:", data.get("model"))
print("\n--- CONVERTED PYTHON CODE ---")
print(data.get("converted_code"))
print("\n--- TARGET PYTHON EXECUTED OUTPUT ---")
print(data.get("target_output"))
print("\n--- OUTPUT PARITY MATCH ---")
print(data.get("output_match"))
