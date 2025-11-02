import anthropic
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_claude_response(message: str, model: str = "claude-sonnet-4-5-20250929") -> str:
    """
    Get response from Claude API.

    Args:
        message: The message to send to Claude
        model: The Claude model to use

    Returns:
        The response from Claude
    """
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": message}]
    )

    return response.content[0].text


def get_llm_response(message: str, llm_type: str, model: Optional[str] = None) -> str:
    """
    Get response from specified LLM.

    Args:
        message: The message to send to the LLM
        llm_type: The type of LLM to use ('claude')
        model: The specific model to use (optional)

    Returns:
        The response from the LLM

    Raises:
        ValueError: If llm_type is not supported
    """
    if llm_type.lower() == "claude":
        if model is None:
            model = "claude-sonnet-4-5-20250929"
        return get_claude_response(message, model)
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")


if __name__ == "__main__":
    # Test the functions
    try:
        # Test get_llm_response with Claude
        response = get_llm_response("What is 2+2?", "claude")
        print(f"Claude response: {response}")

        # Test get_claude_response directly
        response2 = get_claude_response("Tell me a short joke")
        print(f"Direct Claude response: {response2}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set ANTHROPIC_API_KEY environment variable")