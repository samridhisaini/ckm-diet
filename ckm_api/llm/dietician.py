import os
import json
from google import genai
from ckm_api.llm.prompts import SYSTEM_PROMPT, build_user_message

DEFAULT_MODEL = "gemini-2.5-flash"

AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def _get_client():
    use_vertex = os.getenv("USE_VERTEX_AI", "false").lower() == "true"

    if use_vertex:
        project = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION", "us-central1")
        if not project:
            raise EnvironmentError(
                "USE_VERTEX_AI is true but VERTEX_PROJECT_ID is not set in .env"
            )
        return genai.Client(vertexai=True, project=project, location=location)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )
    return genai.Client(api_key=api_key)


def get_diet_advice(patient_json: dict, model: str = DEFAULT_MODEL) -> dict:
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model '{model}'. Choose from: {AVAILABLE_MODELS}")

    client = _get_client()
    user_message = build_user_message(patient_json)
    full_prompt = SYSTEM_PROMPT.strip() + "\n\n" + user_message

    response = client.models.generate_content(model=model, contents=full_prompt)
    raw_text = response.text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON. Raw response:\n{raw_text}\nError: {e}"
        )
