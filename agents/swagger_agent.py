import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# -------------------- Load .env --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_swagger_agent(input: dict) -> dict:
    services = input["services"]
    language = input["language"]
    code_outputs = input["code_outputs"]

    model = genai.GenerativeModel("gemini-1.5-flash")
    swagger_docs = {}

    for service in services:
        controller_code = code_outputs[service]["controller_code"]

        prompt = f"""
        You are an expert in API documentation.

        Given the following controller code written in {language}, generate a Swagger (OpenAPI 3.0) YAML specification.

        Return a JSON object in the following format:
        {{
            "swagger_yaml": "YAML specification here"
        }}

        Controller code:
        \"\"\"
        {controller_code}
        \"\"\"
        """

        response = model.generate_content(prompt)

        raw = response.text.strip()

        # Remove markdown code block wrappers if present
        if raw.startswith("```json"):
            raw = raw.removeprefix("```json").removesuffix("```").strip()
        elif raw.startswith("```"):
            raw = raw.removeprefix("```").removesuffix("```").strip()

        try:
            swagger_docs[service] = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Swagger JSON for service '{service}': {e}\nRaw response:\n{raw}")

    return {
        **input,
        "swagger_outputs": swagger_docs
    }
