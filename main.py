import pandas as pd
import yaml
from typing import List, Tuple
from prompt_optimizer import PromptOptimizer


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


def load_excel_data(file_path: str = "data/golden_data.xlsx", config: dict = None) -> List[Tuple[str, str]]:
    """
    Load input and expected output data from Excel file.

    Args:
        file_path: Path to the Excel file

    Returns:
        List of tuples containing (input_data, expected_output)
    """
    try:
        df = pd.read_excel(file_path)

        # Assume columns are named 'input_data' and 'expected_output'
        # You can modify these column names as needed
        if 'input_data' not in df.columns or 'expected_output' not in df.columns:
            print("⚠️  Warning: Expected columns 'input_data' and 'expected_output' not found.")
            print(f"Available columns: {list(df.columns)}")
            # Try common alternative names
            input_col = next((col for col in df.columns if 'input' in col.lower()), df.columns[0])
            output_col = next((col for col in df.columns if 'output' in col.lower() or 'expected' in col.lower()), df.columns[1])
            print(f"Using columns: '{input_col}' and '{output_col}'")
        else:
            input_col = 'input_data'
            output_col = 'expected_output'

        data_pairs = []
        for _, row in df.iterrows():
            input_data = str(row[input_col]).strip()
            expected_output = str(row[output_col]).strip()
            if input_data and expected_output and input_data != 'nan' and expected_output != 'nan':
                data_pairs.append((input_data, expected_output))

        print(f"📊 Loaded {len(data_pairs)} test cases from Excel file")
        return data_pairs

    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        print("Creating sample data/golden_data.xlsx file...")
        # Create sample file
        sample_data = {
            'input_data': ['What is 2+2?', 'What is the capital of France?', 'Translate "hello" to Spanish'],
            'expected_output': ['4', 'Paris', 'hola']
        }
        df_sample = pd.DataFrame(sample_data)
        df_sample.to_excel(file_path, index=False)
        print(f"✅ Sample file created at {file_path}")
        return [(row['input_data'], row['expected_output']) for _, row in df_sample.iterrows()]


def main():
    """Main function to run the advanced golden prompt generator."""
    print("Welcome to the Advanced Golden Prompt Generator! 🌟")
    print("Featuring: Enhanced Optimization, Feedback Loops & Quality Analytics")
    print("=" * 70)

    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()

    # Get use case from config or user input
    project_config = config.get('project', {})
    if 'use_case' in project_config and project_config['use_case']:
        use_case = project_config['use_case']
        print(f"📝 Using use case from config: {use_case}")
    else:
        use_case = input("\nEnter the use case description: ")

    # Load test data from Excel
    data_config = config.get('data', {})
    excel_file = data_config.get('excel_file', 'data/golden_data.xlsx')
    print(f"📁 Loading test data from {excel_file}...")
    test_data = load_excel_data(excel_file, config)

    if not test_data:
        print("❌ No valid test data found. Please check your Excel file.")
        return

    print(f"\n📊 Loaded {len(test_data)} test cases successfully")

    # Display configuration summary
    optimization_config = config.get('optimization', {})
    if optimization_config:
        print(f"\n🔧 Optimization Settings:")
        print(f"  • Max iterations: {optimization_config.get('max_iterations', 15)}")
        print(f"  • Target success rate: {optimization_config.get('target_success_rate', 100)}%")
        print(f"  • Feedback frequency: every {optimization_config.get('feedback_frequency', 3)} iterations")

    # Display model configuration
    models_config = config.get('models', {})
    if models_config:
        print(f"\n🤖 Model Configuration:")
        for stage, model_config in models_config.items():
            model_name = model_config.get('model', 'default')
            print(f"  • {stage}: {model_name}")

    print(f"\n🚀 Initiating advanced optimization process...")

    # Initialize the PromptOptimizer with config
    optimizer = PromptOptimizer()

    # Create golden prompt using enhanced system
    golden_prompt = optimizer.create_golden_prompt(use_case, test_data)

    if golden_prompt:
        # Final comprehensive validation
        print("\n🔍 Final comprehensive validation...")
        final_matches, total, final_failed = optimizer.test_prompt_with_data(
            golden_prompt, test_data, verbose=False
        )
        final_quality = optimizer.calculate_quality_score(golden_prompt, test_data)

        print(f"\n📊 Final Results:")
        print(f"Success Rate: {final_matches}/{total} ({final_quality['success_rate']:.1f}%)")
        print(f"Overall Quality Score: {final_quality['overall_quality']:.1f}/100")
        print(f"Consistency Score: {final_quality['consistency_score']:.1f}/100")
        print(f"Robustness Score: {final_quality['robustness_score']:.1f}/100")

        if final_failed:
            print(f"\n⚠️  {len(final_failed)} cases still failing - consider manual review")
            print("First few failing cases:")
            for i, (inp, exp, got) in enumerate(final_failed[:3]):
                print(f"  {i+1}. Input: {inp[:30]}... Expected: {exp[:30]}... Got: {got[:30]}...")

        # Save the golden prompt with metadata
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"golden_prompt_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write(f"# Golden Prompt Generated on {pd.Timestamp.now()}\n")
            f.write(f"# Use Case: {use_case}\n")
            f.write(f"# Test Cases: {len(test_data)}\n")
            f.write(f"# Final Success Rate: {final_quality['success_rate']:.1f}%\n")
            f.write(f"# Quality Score: {final_quality['overall_quality']:.1f}/100\n\n")
            f.write(golden_prompt)

        # Also save to the standard filename for backwards compatibility
        with open("golden_prompt.txt", "w") as f:
            f.write(golden_prompt)

        print(f"\n💾 Golden prompt saved to:")
        print(f"  • {filename} (timestamped version)")
        print(f"  • golden_prompt.txt (standard version)")


if __name__ == "__main__":
    main()