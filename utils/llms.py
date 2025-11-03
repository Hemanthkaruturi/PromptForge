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


def get_gpt_response(message: str, model: str = "gpt-4") -> str:
    """
    Get response from OpenAI GPT API.

    Args:
        message: The message to send to GPT
        model: The GPT model to use (e.g., 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo')

    Returns:
        The response from GPT

    Raises:
        ImportError: If openai library is not installed
        ValueError: If OPENAI_API_KEY is not set
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI library not installed. Install it with: pip install openai"
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        max_tokens=4000,
        temperature=0.7
    )

    return response.choices[0].message.content


def get_llm_response(message: str, llm_type: str, model: Optional[str] = None) -> str:
    """
    Router function to get response from specified LLM provider.

    Args:
        message: The message to send to the LLM
        llm_type: The type of LLM provider to use ('claude', 'gpt', or 'openai')
        model: The specific model to use (optional, defaults to provider's default)

    Returns:
        The response from the LLM

    Raises:
        ValueError: If llm_type is not supported

    Supported Providers:
        - 'claude': Anthropic Claude models (claude-sonnet-4-5-20250929, etc.)
        - 'gpt' or 'openai': OpenAI GPT models (gpt-4, gpt-4o, gpt-4-turbo, etc.)

    Examples:
        >>> get_llm_response("What is 2+2?", "claude", "claude-sonnet-4-5-20250929")
        >>> get_llm_response("What is 2+2?", "gpt", "gpt-4")
        >>> get_llm_response("What is 2+2?", "openai", "gpt-4o")
    """
    llm_type_lower = llm_type.lower()

    if llm_type_lower == "claude":
        if model is None:
            model = "claude-sonnet-4-5-20250929"
        return get_claude_response(message, model)

    elif llm_type_lower in ["gpt", "openai"]:
        if model is None:
            model = "gpt-4"
        return get_gpt_response(message, model)

    else:
        raise ValueError(
            f"Unsupported LLM type: {llm_type}. "
            f"Supported types: 'claude', 'gpt', 'openai'"
        )


if __name__ == "__main__":
    # Test the functions
    print("Testing LLM Router Function")
    print("=" * 70)

    # Test Claude
    print("\n1. Testing Claude:")
    print("-" * 70)
    try:
        response = get_llm_response("What is 2+2?", "claude")
        print(f"✅ Claude response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Claude error: {e}")
        print("   Make sure to set ANTHROPIC_API_KEY in .env file")

    # Test GPT
    print("\n2. Testing GPT:")
    print("-" * 70)
    try:
        response = get_llm_response("What is 2+2?", "gpt", "gpt-4")
        print(f"✅ GPT response: {response[:100]}...")
    except ImportError as e:
        print(f"⚠️  GPT not available: {e}")
        print("   Install with: pip install openai")
    except ValueError as e:
        print(f"⚠️  GPT configuration error: {e}")
        print("   Set OPENAI_API_KEY in .env file")
    except Exception as e:
        print(f"❌ GPT error: {e}")

    # Test direct functions
    print("\n3. Testing Direct Function Calls:")
    print("-" * 70)
    try:
        response = get_claude_response("Tell me a short joke")
        print(f"✅ Direct Claude call: {response[:100]}...")
    except Exception as e:
        print(f"❌ Direct Claude error: {e}")

    try:
        response = get_gpt_response("Tell me a short joke", "gpt-4")
        print(f"✅ Direct GPT call: {response[:100]}...")
    except Exception as e:
        print(f"⚠️  Direct GPT error: {e}")

    print("\n" + "=" * 70)
    print("Testing complete!")