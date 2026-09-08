import requests

code = """public class SwapNumbers {
    public static void main(String[] args) {
        float first = 1.20f, second = 2.45f;

        System.out.println("--Before swap--");
        System.out.println("First number = " + first);
        System.out.println("Second number = " + second);

        float temporary = first;
        first = second;
        second = temporary;

        System.out.println("--After swap--");
        System.out.println("First number = " + first);
        System.out.println("Second number = " + second);
    }
}"""

for target in ["python", "c"]:
    print(f"\n=================== TARGET: {target.upper()} ===================")
    r = requests.post(
        "http://localhost:8005/api/v1/interpreter/convert",
        json={"source_code": code, "from_lang": "java", "to_lang": target, "file_name": "SwapNumbers.java"}
    )
    data = r.json()
    print("STATUS:", data.get("status"))
    print("MATCH:", data.get("output_match"))
    print("CONVERTED CODE:\n" + str(data.get("converted_code")))
    print("TARGET STDOUT:\n" + str(data.get("target_output")))
