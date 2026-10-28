import os
import importlib.util

def test_agents_modules_and_functions():
    required = {
        "agents/planning_agent.py": "run_planning_agent",
        "agents/codegen_agent.py": "run_codegen_agent",
        "agents/swagger_agent.py": "run_swagger_agent",
        "agents/test_agent.py": "run_test_agent"
    }

    for path, func in required.items():
        assert os.path.exists(path), f"Missing file: {path}"
        spec = importlib.util.spec_from_file_location("mod", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, func), f"{func} not found in {path}"

def test_agent_functions():
    from agents import planning_agent, codegen_agent, swagger_agent, test_agent

    dummy_story = "Users can register and login."
    dummy_language = "Java"
    dummy_plan = planning_agent.run_planning_agent(dummy_story, dummy_language)
    features = dummy_plan.get("features", [])
    services = dummy_plan.get("services", [])

    dummy_arch_config = {
        "architecture": "REST",
        "database": "MongoDB",
        "messaging": "Kafka",
        "cache": "Redis",
        "api_gateway": "Kong",
        "service_discovery": "Consul"
    }

    code_result = codegen_agent.run_codegen_agent(features, services, dummy_arch_config, dummy_language)
    assert isinstance(code_result, dict), "Codegen agent should return dict"

    swagger_result = swagger_agent.run_swagger_agent(code_result, dummy_language)
    assert isinstance(swagger_result, dict), "Swagger agent should return dict"

    test_result = test_agent.run_test_agent(code_result, dummy_language)
    assert isinstance(test_result, dict), "Test agent should return dict"

def test_output_codegen_directory():
    output_base = "output"
    assert os.path.exists(output_base), "Output folder does not exist"

    service_found = False
    for root, dirs, files in os.walk(output_base):
        for f in files:
            if f.endswith((".java", ".py", ".go", ".yaml", ".ts")):
                service_found = True
                break
    assert service_found, "Expected code or documentation files not found in output directory"

def test_streamlit_ui():
    with open("main.py", encoding="utf-8") as f:
        content = f.read()

    code = content.replace(" ", "").replace("\n", "")
    assert "CodeCrafter AI" in content, "Missing title"
    assert "Enter User Story" in content, "Missing user story label"
    assert "Choose Backend Language" in content, "Missing language label"
    assert "st.text_area" in code, "Missing st.text_area"
    assert "st.selectbox" in code, "Missing st.selectbox"
    assert "st.form_submit_button" in code or "st.button" in code, "Missing st.form_submit_button or st.button"
