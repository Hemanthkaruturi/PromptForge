import pandas as pd
import yaml
import os
import glob
from typing import List, Tuple, Dict, Optional
from utils.llms import get_llm_response
import time


def load_config(config_file: str = "config.yml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"⚠️  Config file {config_file} not found. Using defaults.")
        return {}
    except Exception as e:
        print(f"❌ Error loading config: {e}. Using defaults.")
        return {}


def find_latest_golden_prompt(prompts_dir: str = "golden_prompts") -> Optional[str]:
    """
    Find the latest golden prompt file in the golden_prompts directory.

    Args:
        prompts_dir: Directory containing golden prompt files

    Returns:
        Path to the latest golden prompt file or None if not found
    """
    try:
        # Look for all txt files in the golden_prompts directory
        prompt_files = glob.glob(os.path.join(prompts_dir, "golden_prompt_*.txt"))

        if not prompt_files:
            # Fallback to standard golden_prompt.txt
            standard_prompt = "golden_prompt.txt"
            if os.path.exists(standard_prompt):
                return standard_prompt
            return None

        # Sort by modification time and get the latest
        latest_prompt = max(prompt_files, key=os.path.getmtime)
        return latest_prompt
    except Exception as e:
        print(f"❌ Error finding golden prompt: {e}")
        return None


def load_golden_prompt(prompt_file: str) -> str:
    """
    Load the golden prompt from file.

    Args:
        prompt_file: Path to the golden prompt file

    Returns:
        The golden prompt text
    """
    try:
        with open(prompt_file, "r") as f:
            content = f.read()

        # Remove metadata comments if present
        lines = content.split('\n')
        prompt_lines = []
        metadata_section = True

        for line in lines:
            if metadata_section and line.strip().startswith('#'):
                continue
            elif line.strip() == '':
                continue
            else:
                metadata_section = False
                prompt_lines.append(line)

        return '\n'.join(prompt_lines).strip()
    except Exception as e:
        print(f"❌ Error loading golden prompt: {e}")
        return ""


def load_actual_data(file_path: str = "data/actual_data.xlsx") -> pd.DataFrame:
    """
    Load actual data from Excel file.

    Args:
        file_path: Path to the Excel file with actual data

    Returns:
        DataFrame with actual data
    """
    try:
        df = pd.read_excel(file_path)

        # Check for input_data column
        if 'input_data' not in df.columns:
            # Try to find input column with alternative names
            input_col = next((col for col in df.columns if 'input' in col.lower()), None)
            if input_col:
                df.rename(columns={input_col: 'input_data'}, inplace=True)
            else:
                raise ValueError("No 'input_data' column found in the file")

        print(f"📊 Loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading actual data: {e}")
        raise


def apply_prompt_with_reason(prompt: str, input_data: str, config: dict) -> Tuple[str, str]:
    """
    Apply the golden prompt to generate prediction and reasoning.

    Args:
        prompt: The golden prompt to use
        input_data: The input data to process
        config: Configuration dictionary

    Returns:
        Tuple of (prediction, reason)
    """
    # Get model configuration for answer generation
    models_config = config.get('models', {})
    answer_config = models_config.get('answer_generator', {})
    provider = answer_config.get('provider', 'claude')
    model = answer_config.get('model', 'claude-haiku-4-5-20251001')

    # Create the full prompt with request for reasoning
    full_prompt = f"""{prompt}

Input: {input_data}

Please provide:
1. Your answer/classification
2. A brief explanation of your reasoning

Format your response as:
Answer: [your answer]
Reasoning: [your explanation]"""

    try:
        # Call the LLM
        response = get_llm_response(full_prompt, provider, model)

        # Parse the response to extract answer and reasoning
        answer = ""
        reasoning = ""

        lines = response.strip().split('\n')
        for i, line in enumerate(lines):
            if line.lower().startswith('answer:'):
                answer = line.split(':', 1)[1].strip()
            elif line.lower().startswith('reasoning:'):
                # Get all remaining lines as reasoning
                reasoning = '\n'.join(lines[i:]).split(':', 1)[1].strip()
                break

        # If parsing failed, try to extract answer from first line and use rest as reasoning
        if not answer and response:
            parts = response.strip().split('\n', 1)
            answer = parts[0].strip()
            reasoning = parts[1].strip() if len(parts) > 1 else "No specific reasoning provided"

        return answer, reasoning
    except Exception as e:
        print(f"⚠️  Error processing input: {e}")
        return "ERROR", str(e)


def predict_on_actual_data(
    actual_data_file: str = "data/actual_data.xlsx",
    output_file: str = "data/predicted_data.xlsx",
    prompt_file: Optional[str] = None,
    config: Optional[dict] = None
) -> pd.DataFrame:
    """
    Apply the golden prompt on actual data and generate predictions with reasoning.

    Args:
        actual_data_file: Path to the actual data Excel file
        output_file: Path to save the predictions
        prompt_file: Path to the golden prompt file (if None, uses latest)
        config: Configuration dictionary (if None, loads from config.yml)

    Returns:
        DataFrame with predictions
    """
    print("🚀 Starting prediction process...")
    print("=" * 70)

    # Load configuration
    if config is None:
        config = load_config()

    # Find and load golden prompt
    if prompt_file is None:
        print("🔍 Finding latest golden prompt...")
        prompt_file = find_latest_golden_prompt()
        if prompt_file is None:
            print("\n" + "=" * 70)
            print("❌ ERROR: No golden prompt found!")
            print("=" * 70)
            print("\nYou need to generate a golden prompt first before running predictions.\n")
            print("📋 Steps to generate a golden prompt:")
            print("   1. Prepare your training data in data/golden_data.xlsx")
            print("      - Must have 'input_data' and 'expected_output' columns")
            print("      - Optionally add 'reason' column for better results")
            print()
            print("   2. Generate the golden prompt using one of these methods:")
            print("      • Command line: python main.py")
            print("      • Web interface: streamlit run app.py")
            print()
            print("   3. Once generated, run this script again: python predict.py")
            print()
            print("💡 Tip: Check if golden_prompt.txt or golden_prompts/ directory exists")
            print("=" * 70)
            raise FileNotFoundError("No golden prompt found. Please generate one first using 'python main.py' or 'streamlit run app.py'")

    print(f"📄 Using golden prompt: {prompt_file}")
    golden_prompt = load_golden_prompt(prompt_file)

    if not golden_prompt:
        print("\n" + "=" * 70)
        print("❌ ERROR: Golden prompt file is empty!")
        print("=" * 70)
        print(f"\nThe file '{prompt_file}' exists but appears to be empty or corrupted.\n")
        print("📋 Suggested actions:")
        print("   1. Check the file manually to see if it contains a prompt")
        print("   2. Regenerate the golden prompt: python main.py")
        print("   3. Verify your training data in data/golden_data.xlsx")
        print("=" * 70)
        raise ValueError(f"Golden prompt file '{prompt_file}' is empty or could not be loaded")

    print(f"✅ Golden prompt loaded successfully")
    print(f"Prompt preview: {golden_prompt[:100]}...")

    # Load actual data
    print(f"\n📁 Loading actual data from {actual_data_file}...")
    df = load_actual_data(actual_data_file)

    # Prepare results
    predictions = []
    reasons = []

    # Get rate limiting configuration
    performance_config = config.get('performance', {})
    rate_limit_delay = performance_config.get('rate_limit_delay', 1.0)

    # Process each input
    total = len(df)
    print(f"\n🔄 Processing {total} records...")
    print("-" * 70)

    for idx, row in df.iterrows():
        input_data = str(row['input_data']).strip()

        print(f"Processing {idx+1}/{total}: {input_data[:50]}...")

        # Apply rate limiting
        if idx > 0 and rate_limit_delay > 0:
            time.sleep(rate_limit_delay)

        # Get prediction and reasoning
        prediction, reason = apply_prompt_with_reason(golden_prompt, input_data, config)

        predictions.append(prediction)
        reasons.append(reason)

        print(f"  ✅ Prediction: {prediction}")
        print(f"  📝 Reasoning: {reason[:80]}...")

    # Add predictions to dataframe
    df['predicted_output'] = predictions
    df['reason'] = reasons

    # Save results
    print(f"\n💾 Saving predictions to {output_file}...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_excel(output_file, index=False)

    print(f"✅ Predictions saved successfully!")
    print(f"\n📊 Summary:")
    print(f"  • Total records processed: {total}")
    print(f"  • Output file: {output_file}")
    print(f"  • Columns: {list(df.columns)}")

    return df


def main():
    """Main function to run predictions."""
    print("🌟 Golden Prompt Prediction Tool")
    print("=" * 70)

    # Load configuration
    config = load_config()

    # Check for golden prompt early
    print("\n🔍 Checking for golden prompt...")
    prompt_file = find_latest_golden_prompt()
    if prompt_file:
        print(f"✅ Found golden prompt: {prompt_file}")
    else:
        print("\n" + "=" * 70)
        print("⚠️  WARNING: No golden prompt found!")
        print("=" * 70)
        print("\nPlease generate a golden prompt first:\n")
        print("  Option 1: python main.py")
        print("  Option 2: streamlit run app.py")
        print("\nThen run this script again: python predict.py")
        print("=" * 70)
        return  # Exit gracefully

    # Get file paths from config or use defaults
    data_config = config.get('data', {})
    actual_data_file = data_config.get('actual_data_file', 'data/actual_data.xlsx')
    predicted_data_file = data_config.get('predicted_data_file', 'data/predicted_data.xlsx')

    # Check if actual data file exists
    if not os.path.exists(actual_data_file):
        print(f"\n⚠️  Actual data file not found: {actual_data_file}")
        print("Creating sample actual_data.xlsx...")

        # Create sample data
        sample_data = {
            'input_data': [
                'A fintech startup developing mobile payment solutions with cloud infrastructure and APIs',
                'A local grocery store using a simple POS system',
                'A healthcare provider using electronic health records and telemedicine platforms'
            ]
        }
        df_sample = pd.DataFrame(sample_data)
        os.makedirs('data', exist_ok=True)
        df_sample.to_excel(actual_data_file, index=False)
        print(f"✅ Sample file created at {actual_data_file}")

    # Run predictions
    try:
        result_df = predict_on_actual_data(
            actual_data_file=actual_data_file,
            output_file=predicted_data_file,
            config=config
        )

        print("\n🎉 Prediction completed successfully!")
        print("\nFirst few predictions:")
        print(result_df[['input_data', 'predicted_output']].head().to_string(index=False))

    except FileNotFoundError as e:
        # This error is already well-explained above, just exit cleanly
        return
    except ValueError as e:
        # This error is already well-explained above, just exit cleanly
        return
    except Exception as e:
        print(f"\n❌ Unexpected error during prediction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
