from dotenv import load_dotenv
import os
import re
import json
import google.generativeai as genai

# -------------------- Load .env --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_test_agent(input):
    outputs = input["code_outputs"]
    language = input["language"]
    test_files = {}

    for service, files in outputs.items():
        prompt = f"""
Generate unit tests in {language} using the standard test framework.

Controller code:
{files["controller_code"]}

Service code:
{files["service_code"]}

Respond in JSON:
{{ "test_filename": "...", "test_code": "..." }}
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        test_files[service] = extract_first_json_block(response.text)

    return {**input, "test_outputs": test_files}



def extract_first_json_block(text: str) -> dict:
    try:
        # Step 1: Extract the JSON block
        match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON block found.")
        json_str = match.group(1)

        # Step 2: Sanitize the JSON string: escape unescaped internal quotes
        def escape_unescaped_quotes(s):
            def replacer(m):
                # Skip already escaped quotes
                if m.group(0).startswith('\\"'):
                    return m.group(0)
                return m.group(0).replace('"', '\\"')
            
            # Target the `test_code` field specifically
            pattern = r'("test_code"\s*:\s*")(.*?)(")(?=,\s*")'  # captures value of test_code
            return re.sub(pattern, lambda m: m.group(1) + m.group(2).replace('"', '\\"') + m.group(3), s, flags=re.DOTALL)

        json_str = escape_unescaped_quotes(json_str)

        # Step 3: Parse and return the JSON
        return json.loads(json_str)

    except Exception as e:
        raise ValueError(f"Failed to extract JSON from text:\n{text}\n\nError: {e}")
