import yaml
import re
from typing import Dict, List, Tuple, Optional
from utils.llms import get_llm_response


class PromptOptimizer:
    """
    Core prompt optimization engine that generates and refines prompts
    based on use case, input data, and expected output data.
    """

    def __init__(self, config_file: str = "config.yml", prompts_file: Optional[str] = None):
        """Initialize the PromptOptimizer with configuration."""
        self.config = self._load_config(config_file)

        # Use custom prompts file if specified, otherwise use default or config setting
        if prompts_file:
            self.prompts_file = prompts_file
        elif self.config.get('advanced', {}).get('custom_prompts_file'):
            self.prompts_file = self.config['advanced']['custom_prompts_file']
        else:
            self.prompts_file = "prompts/prompts.yml"

        self.prompts = self._load_prompts()
        self._validate_config()

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found. Using default settings.")
            return self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}. Using default settings.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is not found."""
        return {
            'optimization': {
                'max_iterations': 15,
                'target_success_rate': 100,
                'feedback_frequency': 3
            },
            'models': {
                'initial_prompt_generator': {'provider': 'claude', 'model': 'claude-sonnet-4-5-20250929'},
                'answer_generator': {'provider': 'claude', 'model': 'claude-3-5-sonnet-20241022'},
                'prompt_optimizer': {'provider': 'claude', 'model': 'claude-sonnet-4-5-20250929'},
                'feedback_collector': {'provider': 'claude', 'model': 'claude-3-5-sonnet-20241022'},
                'prompt_evolver': {'provider': 'claude', 'model': 'claude-sonnet-4-5-20250929'}
            },
            'matching': {'case_sensitive': False, 'strip_whitespace': True},
            'output': {'verbose_logging': True}
        }

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompts from YAML file."""
        with open(self.prompts_file, "r") as file:
            return yaml.safe_load(file)

    def _validate_config(self):
        """Validate configuration parameters."""
        if self.config.get('validation', {}).get('validate_config', True):
            # Validate required sections
            required_sections = ['optimization', 'models']
            for section in required_sections:
                if section not in self.config:
                    raise ValueError(f"Missing required config section: {section}")

    def _get_model_config(self, stage: str) -> Dict:
        """Get model configuration for a specific stage."""
        return self.config['models'].get(stage, {
            'provider': 'claude',
            'model': 'claude-3-5-sonnet-20241022'
        })

    def _call_llm(self, prompt: str, stage: str) -> str:
        """Call LLM with stage-specific model configuration."""
        model_config = self._get_model_config(stage)
        provider = model_config.get('provider', 'claude')
        model = model_config.get('model', 'claude-3-5-sonnet-20241022')

        return get_llm_response(prompt, provider, model)

    def _extract_prompt_from_response(self, response: str) -> str:
        """Extract prompt from LLM response between START and END markers."""
        pattern = r"START\s*<prompt>\s*(.*?)\s*</prompt>\s*END"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return response.strip()

    def generate_initial_prompt(self, use_case: str, input_data: str, output_data: str) -> str:
        """Generate initial prompt using the enhanced prompt generator."""
        prompt_template = self.prompts["INITIAL_PROMPT_GENERATOR"]

        formatted_prompt = prompt_template.format(
            use_case=use_case,
            input_data=input_data,
            output_data=output_data
        )

        response = self._call_llm(formatted_prompt, "initial_prompt_generator")
        return self._extract_prompt_from_response(response)

    def generate_answer(self, prompt: str, input_data: str) -> str:
        """Generate answer using the given prompt."""
        answer_template = self.prompts["ANSWER_GENERATOR"]

        formatted_prompt = answer_template.format(
            prompt=prompt,
            input_data=input_data
        )

        return self._call_llm(formatted_prompt, "answer_generator")

    def optimize_prompt(self, current_prompt: str, input_data: str,
                       actual_output: str, expected_output: str) -> str:
        """Optimize prompt based on the mismatch between actual and expected output."""
        optimizer_template = self.prompts["PROMPT_OPTIMIZER"]

        formatted_prompt = optimizer_template.format(
            prompt=current_prompt,
            input_data=input_data,
            output_data=actual_output,
            actual_output=expected_output
        )

        response = self._call_llm(formatted_prompt, "prompt_optimizer")
        return self._extract_prompt_from_response(response)

    def collect_feedback(self, prompt: str, success_rate: float, successful_cases: int,
                        total_cases: int, failed_cases: List[Tuple[str, str, str]]) -> str:
        """Collect comprehensive feedback on prompt performance."""
        feedback_template = self.prompts["FEEDBACK_COLLECTOR"]

        # Format failed cases for analysis
        failed_cases_text = "\n".join([
            f"Input: {input_data}\nExpected: {expected}\nGot: {actual}\n---"
            for input_data, expected, actual in failed_cases[:5]  # Limit to 5 examples
        ])

        formatted_prompt = feedback_template.format(
            prompt=prompt,
            success_rate=success_rate,
            successful_cases=successful_cases,
            total_cases=total_cases,
            failed_cases=failed_cases_text
        )

        return get_llm_response(formatted_prompt, "claude")

    def evolve_prompt(self, current_prompt: str, feedback: str,
                     success_rate: float, iteration: int) -> str:
        """Evolve prompt based on comprehensive feedback."""
        evolver_template = self.prompts["PROMPT_EVOLVER"]

        formatted_prompt = evolver_template.format(
            prompt=current_prompt,
            feedback=feedback,
            success_rate=success_rate,
            iteration=iteration
        )

        response = get_llm_response(formatted_prompt, "claude")
        return self._extract_prompt_from_response(response)

    def check_output_match(self, actual_output: str, expected_output: str) -> bool:
        """Check if actual output matches expected output."""
        return actual_output.strip().lower() == expected_output.strip().lower()

    def test_prompt_with_data(self, prompt: str, test_data: List[Tuple[str, str]],
                             verbose: bool = True) -> Tuple[int, int, List[Tuple[str, str, str]]]:
        """
        Test a prompt against all test cases.

        Args:
            prompt: The prompt to test
            test_data: List of (input_data, expected_output) tuples
            verbose: Whether to print detailed results

        Returns:
            Tuple of (successful_matches, total_tests, failed_cases)
        """
        successful_matches = 0
        total_tests = len(test_data)
        failed_cases = []

        for i, (input_data, expected_output) in enumerate(test_data):
            actual_output = self.generate_answer(prompt, input_data)

            if self.check_output_match(actual_output, expected_output):
                successful_matches += 1
                if verbose:
                    print(f"   ✅ Test {i+1}/{total_tests}: Match found")
            else:
                failed_cases.append((input_data, expected_output, actual_output))
                if verbose:
                    print(f"   ❌ Test {i+1}/{total_tests}: Mismatch")
                    print(f"      Expected: {expected_output[:50]}...")
                    print(f"      Got: {actual_output[:50]}...")

        return successful_matches, total_tests, failed_cases

    def calculate_quality_score(self, prompt: str, test_data: List[Tuple[str, str]]) -> Dict[str, float]:
        """Calculate comprehensive quality metrics for a prompt."""
        successful_matches, total_tests, _ = self.test_prompt_with_data(
            prompt, test_data, verbose=False
        )

        # Basic metrics
        success_rate = (successful_matches / total_tests) * 100 if total_tests > 0 else 0

        # Advanced metrics (simplified for now)
        consistency_score = success_rate  # Could be enhanced with variance analysis
        robustness_score = success_rate   # Could be enhanced with edge case analysis

        return {
            "success_rate": success_rate,
            "successful_cases": successful_matches,
            "total_cases": total_tests,
            "consistency_score": consistency_score,
            "robustness_score": robustness_score,
            "overall_quality": (success_rate + consistency_score + robustness_score) / 3
        }

    def create_golden_prompt(self, use_case: str, test_data: List[Tuple[str, str]],
                           max_iterations: int = 15) -> str:
        """
        Create a golden prompt through iterative optimization with advanced feedback loops.

        Args:
            use_case: Description of the task
            test_data: List of (input_data, expected_output) tuples
            max_iterations: Maximum number of optimization iterations

        Returns:
            The optimized golden prompt
        """
        if not test_data:
            print("❌ No test data available!")
            return ""

        print(f"🚀 Starting advanced golden prompt creation for: {use_case}")
        print(f"📊 Testing against {len(test_data)} test cases")
        print(f"🎯 Target: 100% success rate with intelligent optimization")
        print("-" * 70)

        # Use first test case to generate initial prompt
        sample_input, sample_output = test_data[0]
        print("🔨 Generating initial prompt with enhanced analysis...")
        current_prompt = self.generate_initial_prompt(use_case, sample_input, sample_output)
        print("✅ Initial prompt created")

        best_prompt = current_prompt
        best_quality_score = 0
        performance_history = []
        iteration = 0

        # Enhanced optimization loop with feedback
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}")

            # Test current prompt and collect detailed results
            successful_matches, total_tests, failed_cases = self.test_prompt_with_data(
                current_prompt, test_data, verbose=True
            )

            # Calculate comprehensive quality metrics
            quality_metrics = self.calculate_quality_score(current_prompt, test_data)
            success_rate = quality_metrics["success_rate"]
            overall_quality = quality_metrics["overall_quality"]

            print(f"📈 Performance: {successful_matches}/{total_tests} ({success_rate:.1f}%)")
            print(f"🎯 Quality Score: {overall_quality:.1f}/100")

            # Track performance history
            performance_history.append({
                "iteration": iteration,
                "success_rate": success_rate,
                "quality_score": overall_quality,
                "prompt": current_prompt
            })

            # Update best prompt based on overall quality, not just success rate
            if overall_quality > best_quality_score:
                best_quality_score = overall_quality
                best_prompt = current_prompt
                print(f"🏆 New best prompt! Quality score: {overall_quality:.1f}")

            # Perfect score achieved
            if successful_matches == total_tests:
                print(f"\n🎉 Perfect score achieved! Golden prompt ready.")
                break

            # Advanced feedback-based optimization every 3 iterations
            if iteration % 3 == 0 and iteration > 2:
                print(f"🔍 Collecting comprehensive feedback for systematic improvement...")
                feedback = self.collect_feedback(
                    current_prompt, success_rate, successful_matches, total_tests, failed_cases
                )

                print(f"🌱 Evolving prompt based on comprehensive analysis...")
                current_prompt = self.evolve_prompt(current_prompt, feedback, success_rate, iteration)
                print(f"✅ Prompt evolved using advanced feedback")
            else:
                # Standard optimization for immediate failures
                if failed_cases:
                    # Use the most representative failed case
                    input_data, expected_output, actual_output = failed_cases[0]
                    print(f"🔧 Optimizing based on failed case...")
                    current_prompt = self.optimize_prompt(
                        current_prompt, input_data, actual_output, expected_output
                    )
                else:
                    # This shouldn't happen if we didn't achieve 100%
                    break

        # Final analysis and reporting
        final_quality = best_quality_score
        final_success_rate = performance_history[-1]["success_rate"] if performance_history else 0

        print(f"\n📊 Optimization Complete!")
        print(f"Final Quality Score: {final_quality:.1f}/100")
        print(f"Final Success Rate: {final_success_rate:.1f}%")
        print(f"Total Iterations: {iteration}")

        if final_success_rate == 100:
            print(f"🎉 Perfect golden prompt achieved!")
        elif final_quality >= 85:
            print(f"🏆 High-quality golden prompt achieved!")
        else:
            print(f"⚠️  Optimization completed with room for improvement")

        print(f"\n🏆 Final Golden Prompt:")
        print("-" * 70)
        print(best_prompt)
        print("-" * 70)

        return best_prompt


if __name__ == "__main__":
    """
    Test the PromptOptimizer with direct input.
    Run this file directly to test the core optimization functionality.
    """
    print("🧪 PromptOptimizer Test Mode")
    print("=" * 50)

    # Get inputs from user
    use_case = input("Enter the use case description: ")

    print("\nEnter test data (input and expected output pairs)")
    print("Type 'done' when finished adding test cases")

    test_data = []
    case_num = 1

    while True:
        print(f"\n--- Test Case {case_num} ---")
        input_data = input("Input data: ").strip()

        if input_data.lower() == 'done':
            break

        expected_output = input("Expected output: ").strip()

        if input_data and expected_output:
            test_data.append((input_data, expected_output))
            case_num += 1
            print("✅ Test case added")
        else:
            print("❌ Invalid input, skipping...")

    if not test_data:
        print("❌ No test data provided. Exiting.")
        exit(1)

    print(f"\n📊 Total test cases: {len(test_data)}")

    # Initialize optimizer and create golden prompt
    optimizer = PromptOptimizer()

    print("\n🚀 Starting optimization...")
    golden_prompt = optimizer.create_golden_prompt(use_case, test_data)

    if golden_prompt:
        # Save the result
        filename = "test_golden_prompt.txt"
        with open(filename, "w") as f:
            f.write(f"# Test Golden Prompt\n")
            f.write(f"# Use Case: {use_case}\n")
            f.write(f"# Test Cases: {len(test_data)}\n\n")
            f.write(golden_prompt)

        print(f"\n💾 Golden prompt saved to: {filename}")

        # Final test
        print(f"\n🔍 Final validation:")
        final_matches, total, failed_cases = optimizer.test_prompt_with_data(
            golden_prompt, test_data, verbose=True
        )
        quality = optimizer.calculate_quality_score(golden_prompt, test_data)

        print(f"\n📊 Final Results:")
        print(f"✅ Success Rate: {final_matches}/{total} ({quality['success_rate']:.1f}%)")
        print(f"🎯 Quality Score: {quality['overall_quality']:.1f}/100")
    else:
        print("❌ Failed to generate golden prompt")