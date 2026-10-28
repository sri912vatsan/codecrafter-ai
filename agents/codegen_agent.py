import json
import os 
import re
import google.generativeai as genai
from dotenv import load_dotenv

# -------------------- Load .env --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_codegen_agent(input: dict) -> dict:
    features = input["features"]
    services = input["services"]
    arch_config = input["architecture"]
    language = input["language"]

    model = genai.GenerativeModel("gemini-1.5-flash")
    outputs = {}

    for feature, service in zip(features, services):
        prompt = f"""
        Generate backend code for the following microservice.

        Feature: {feature}
        Service Name: {service}
        Language: {language}
        Architecture Style: {arch_config.get('style')}
        Database: {arch_config.get('database')}
        Messaging Queue: {arch_config.get('message_queue')}
        Cache: {arch_config.get('cache')}

        Return ONLY a valid JSON object with the following keys:
        {{
            "controller_filename": "...",
            "controller_code": "...",
            "service_filename": "...",
            "service_code": "...",
            "model_filename": "...",
            "model_code": "..."
        }}
        No explanations. No markdown. Just JSON.
        """

        try:
            response = model.generate_content(prompt)
            print(f"🔍 Raw response from Gemini for {service}:\n{response.text}")
            raw = response.text
            parsed = extract_first_json_block(raw)
            outputs[service] = parsed
        except Exception as e:
            raise ValueError(f"Invalid JSON for service '{service}': {e}\nRaw response:\n{response.text}")

    return {
        **input,
        "code_outputs": outputs
    }


def extract_first_json_block(text: str):
    """
    Clean Gemini LLM output and extract the first valid JSON block.
    Handles markdown code fences and avoids regex recursion.
    """
    text = text.strip()

    # Remove Markdown code block wrappers (e.g., ```json ... ```)
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Try to parse directly
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from Gemini output:\n{e}\n\nRaw:\n{text}")
