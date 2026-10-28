# CodeCrafter AI: GenAI-Powered Microservice Builder

CodeCrafter AI turns a plain-English user story into a set of microservices. It uses Google Gemini to plan the services, generate controller, service, and model code, write OpenAPI (Swagger) specifications, and produce unit tests, all through a small Streamlit web interface.

## Features

- Converts a user story into features, microservices, and a recommended architecture
- Generates controller, service, and model code for each microservice
- Produces an OpenAPI 3.0 specification per service from its controller code
- Generates unit tests per service
- Saves every artifact to a structured `output/` folder
- Supports Java, Node.js, and Python as the target backend language

## How It Works

The generation pipeline runs four agents in sequence. Each agent receives the output of the previous one.

1. Planning agent (`agents/planning_agent.py`) analyzes the user story and returns features, services, and an architecture recommendation (architecture style, database, messaging, cache, API gateway, and service discovery).
2. Code generation agent (`codegen` stage) produces the controller, service, and model code for each service.
3. Swagger agent (`agents/swagger_agent.py`) writes an OpenAPI 3.0 YAML specification from each controller.
4. Test agent (`agents/test_agent.py`) writes unit tests for each service's controller and service code.

The Streamlit app in `main.py` shows the extracted features, services, and architecture, then previews the generated code for each service.

## Project Structure

```text
codecrafterAI/
├── main.py                  # Streamlit app (sequential agent pipeline)
├── main_lg.py               # Streamlit app using a LangGraph pipeline (experimental)
├── tests.py                 # pytest suite
├── installation.txt         # Dependency list
├── agents/
│   ├── planning_agent.py    # Story to features, services, and architecture
│   ├── swagger_agent.py     # Controller code to OpenAPI YAML
│   └── test_agent.py        # Service code to unit tests
└── output/                  # Generated projects, one folder per user story
```

Each user story produces a folder under `output/` named from a slug of the story text:

```text
output/<story_slug>/
├── <ServiceName>/           # controller, service, and model files
├── swagger/<ServiceName>/swagger.yaml
└── tests/<ServiceName>/     # unit test file
```

## Prerequisites

- Python 3.10 or newer
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

## Installation

Clone the repository and move into the project folder:

```bash
git clone <your-repository-url>
cd codecrafterAI/codecrafterAI
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install the dependencies:

```bash
pip install streamlit google-generativeai==0.4.1 python-dotenv==1.0.1 langgraph pytest
```

## Configuration

Create a `.env` file in the project folder and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file. Add it to `.gitignore` so that the key stays private.

## Usage

Start the Streamlit app:

```bash
streamlit run main.py
```

Then open the URL shown in the terminal (by default `http://localhost:8501`), enter a user story, choose a backend language, and click Generate Microservices.

Example user story:

```text
Users can register, log in, and view their profile. Admins can add, edit, and delete users.
```

When generation finishes, the generated files are saved to `output/<story_slug>/`.

## Running Tests

The test suite is in `tests.py` and uses pytest. The tests call the Gemini API, so set `GEMINI_API_KEY` before running them:

```bash
pytest tests.py
```

## Notes

- `main_lg.py` is an experimental version that wires the same agents into a LangGraph state graph. Use `main.py` for the supported workflow.
- Generated code is a starting point. Review it, add error handling and security controls, and run it against your own build and test setup before use.
- Generation quality depends on the Gemini model and the prompts in each agent. Large or vague user stories may produce incomplete output.
