import os
import sys

# Pre-pend phase4 path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase4_generation')))
from generator import RAGGenerator

def run_integration_tests():
    print("Initializing RAG Pipeline (Phases 2 -> 3 -> 4)...")
    generator = RAGGenerator()
    
    test_cases = [
        {
            "name": "HDFC Flexi Cap Exit Load",
            "query": "What is the exit load of HDFC flexi cap fund ?",
            "expected_keywords": [
                "1.0%",
                "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184"
            ]
        },
        {
            "name": "SBI ELSS Minimum SIP",
            "query": "What is the minimum SIP for SBI ELSS Tax Saver Fund?",
            "expected_keywords": [
                "500",
                "https://www.indmoney.com/mutual-funds/sbi-elss-tax-saver-fund-direct-growth-2754"
            ]
        },
        {
            "name": "Out of Scope Guardrail",
            "query": "What is the capital of France?",
            "expected_keywords": [
                "out of scope" # Or some variation expecting a refusal
            ]
        }
    ]

    passed_tests = 0

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("\nStarting Integration Tests...\n")
        f.write("-" * 50 + "\n")
        
        for i, test in enumerate(test_cases):
            f.write(f"Test {i+1}: {test['name']}\n")
            f.write(f"Query: {test['query']}\n")
            
            answer = generator.generate_answer(test['query'])
            f.write(f"LLM Answer:\n{answer}\n")
            
            # Verify keywords
            missing_keywords = []
            for kw in test['expected_keywords']:
                if kw.lower() == "out of scope":
                    if "out of scope" not in answer.lower() and "out of the scope" not in answer.lower() and "i do not have enough information" not in answer.lower():
                       missing_keywords.append("guardrail triggered")
                elif kw not in answer:
                    missing_keywords.append(kw)
                    
            if not missing_keywords:
                f.write("Status: [PASS] \u2705\n")
                passed_tests += 1
            else:
                f.write(f"Status: [FAIL] \u274C - Missing expected keywords: {missing_keywords}\n")
            f.write("-" * 50 + "\n")
            
        f.write(f"\nIntegration Test Summary: {passed_tests}/{len(test_cases)} Passed\n")
    print(f"Tests complete. Details written to results.txt. Total passed: {passed_tests}/{len(test_cases)}")

if __name__ == "__main__":
    # Handle UTF-8 encoding on Windows console
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    run_integration_tests()
