import sys
from app.services.ast_transpiler import DeterministicTranspiler

java_code = """import java.util.Scanner;

public class Main {
    public static int calculateSum(int[] numbers) {
        int total = 0;
        for (int n : numbers) {
            total += n;
        }
        return total;
    }

    public static void main(String[] args) {
        int[] arr = {10, 20, 30, 40, 50};
        int sum = calculateSum(arr);
        System.out.println("Sum: " + sum);

        for (int i = 1; i <= 5; i++) {
            if (i % 2 == 0) {
                System.out.println("Even: " + i);
            } else {
                System.out.println("Odd: " + i);
            }
        }
    }
}"""

py_code = DeterministicTranspiler.transpile(java_code, "java", "python")

print("--- GENERATED PYTHON CODE ---")
print(py_code)

print("\n--- EXECUTING PYTHON CODE ---")
exec(py_code)
