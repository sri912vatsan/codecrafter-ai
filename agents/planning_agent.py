import streamlit as st
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load Gemini API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Import agents
from agents.planning_agent import run_planning_agent
from agents.codegen_agent import run_codegen_agent
from agents.swagger_agent import run_swagger_agent
from agents.test_agent import run_test_agent


# -------------------- Helpers --------------------

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '_', text.lower())


def save_outputs(result, story_slug):
    base_path = f"output/{story_slug}"
    os.makedirs(base_path, exist_ok=True)

    code_outputs = result["code_outputs"]
    swagger_outputs = result["swagger_outputs"]
    test_outputs = result["test_outputs"]

    for service, files in code_outputs.items():
        svc_dir = os.path.join(base_path, service)
        os.makedirs(svc_dir, exist_ok=True)

        with open(os.path.join(svc_dir, files["controller_filename"]), "w") as f:
            f.write(files["controller_code"])
        with open(os.path.join(svc_dir, files["service_filename"]), "w") as f:
            f.write(files["service_code"])
        with open(os.path.join(svc_dir, files["model_filename"]), "w") as f:
            f.write(files["model_code"])

    for service, swagger in swagger_outputs.items():
        swagger_dir = os.path.join(base_path, "swagger", service)
        os.makedirs(swagger_dir, exist_ok=True)
        with open(os.path.join(swagger_dir, "swagger.yaml"), "w") as f:
            f.write(swagger["swagger_yaml"])

    for service, test in test_outputs.items():
        test_dir = os.path.join(base_path, "tests", service)
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, test["test_filename"]), "w") as f:
            f.write(test["test_code"])

    return base_path


# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="GenAI Microservice Builder", layout="wide")
st.title("CodeCrafter AI: GenAI-Powered Microservice Builder")

story = st.text_area("Enter User Story")
language = st.selectbox("Choose Backend Language:", ["Java", "NodeJS", "Python"])

if st.button("Generate Microservices"):
    if story and language:
        story_slug = slugify(story)

        with st.spinner("Running all agents..."):

            # Run agents in sequence manually
            result1 = run_planning_agent({"user_story": story, "language": language})
            result2 = run_codegen_agent(result1)
            result3 = run_swagger_agent(result2)
            result4 = run_test_agent(result3)

            output_path = save_outputs(result4, story_slug)

        st.success(f" Microservices generated successfully under `output/{story_slug}`!")

        # ----------- Output Visualization ------------
        st.subheader("Features & Services")
        features = result4.get("features", [])
        services = result4.get("services", [])
        arch = result4.get("architecture", {})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Features**")
            st.write(features)
        with col2:
            st.markdown("**Services**")
            st.write(services)

        st.markdown("**User Specified Architecture Hints**")
        st.json(arch)

        st.subheader("Generated Code Perview")

        code_outputs = result4["code_outputs"]
        swagger_outputs = result4["swagger_outputs"]
        test_outputs = result4["test_outputs"]

        for service in services:
            st.markdown(f"### 🔹 {service}")
            with st.expander("Controller Code"):
                st.code(code_outputs[service]["controller_code"], language.lower())
            with st.expander("Service Logic"):
                st.code(code_outputs[service]["service_code"], language.lower())
            with st.expander("Model Definition"):
                st.code(code_outputs[service]["model_code"], language.lower())
            with st.expander("Swagger (OpenAPI)"):
                st.code(swagger_outputs[service]["swagger_yaml"], language="yaml")
            with st.expander("Unit Test Code"):
                st.code(test_outputs[service]["test_code"], language.lower())

        st.success("Code generation complete!")
        st.markdown(f" View saved files at: `output/{story_slug}/`")
