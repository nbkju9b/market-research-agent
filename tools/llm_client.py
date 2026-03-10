import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client() -> OpenAI:
    """Returns an OpenRouter client using the OpenAI-compatible API."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )


def call_llm(prompt: str, model: str = "openrouter/auto", max_tokens: int = 4000) -> str:
    """
    Single reusable function all agents will use to call the LLM.
    Easy to swap model in one place.
    """
    client = get_llm_client()
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    # useful for debugging which free model openrouter picked
    actual_model = response.model
    print(f"[llm] model used: {actual_model}")

    actual_model = response.model
    print(f"Model used: {actual_model}")
    return response.choices[0].message.content    


   

if __name__ == "__main__":
    result = call_llm("In one sentence, what is a hedge fund?")
    print(result)