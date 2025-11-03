import streamlit as st
import pandas as pd
import yaml
import os
import json
from typing import List, Tuple
from prompt_optimizer import PromptOptimizer
from io import StringIO
import time

# Page configuration
st.set_page_config(
    page_title="Golden Prompt Generator",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stProgress .st-bo {
        background-color: #00D4FF;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
    }
    </style>
""", unsafe_allow_html=True)


def load_config(config_file: str = "config.yml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.warning(f"Config file {config_file} not found. Using defaults.")
        return {}
    except Exception as e:
        st.error(f"Error loading config: {e}. Using defaults.")
        return {}


def save_config(config: dict, config_file: str = "config.yml"):
    """Save configuration to YAML file."""
    try:
        with open(config_file, "w") as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        st.error(f"Error saving config: {e}")
        return False


def load_excel_data(file_path: str = None, uploaded_file=None) -> Tuple[List[Tuple], pd.DataFrame]:
    """
    Load input and expected output data from Excel file.
    Optionally includes reason column if present.

    Returns:
        Tuple of (data_pairs, dataframe)
        where data_pairs is a list of tuples: (input_data, expected_output) or (input_data, expected_output, reason)
    """
    try:
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
        elif file_path:
            df = pd.read_excel(file_path)
        else:
            return [], None

        # Try to find input and output columns
        if 'input_data' not in df.columns or 'expected_output' not in df.columns:
            # Try common alternative names
            input_col = next((col for col in df.columns if 'input' in col.lower()), df.columns[0])
            output_col = next((col for col in df.columns if 'output' in col.lower() or 'expected' in col.lower()), df.columns[1])
        else:
            input_col = 'input_data'
            output_col = 'expected_output'

        # Check if reason column exists
        has_reason = 'reason' in df.columns

        data_pairs = []
        for _, row in df.iterrows():
            input_data = str(row[input_col]).strip()
            expected_output = str(row[output_col]).strip()
            if input_data and expected_output and input_data != 'nan' and expected_output != 'nan':
                if has_reason:
                    reason = str(row['reason']).strip()
                    # Only include reason if it's not empty or 'nan'
                    if reason and reason != 'nan':
                        data_pairs.append((input_data, expected_output, reason))
                    else:
                        data_pairs.append((input_data, expected_output))
                else:
                    data_pairs.append((input_data, expected_output))

        return data_pairs, df

    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return [], None


def main():
    # Title and description
    st.title("🌟 Golden Prompt Generator")
    st.markdown("""
    Welcome to the **Advanced Golden Prompt Generator**! This tool helps you create optimized prompts
    through iterative testing and refinement.
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Load existing config
        config = load_config()

        # Project Settings
        st.subheader("📋 Project Settings")
        project_name = st.text_input(
            "Project Name",
            value=config.get('project', {}).get('name', 'Golden Prompt Generator')
        )
        project_version = st.text_input(
            "Version",
            value=config.get('project', {}).get('version', '2.0.0')
        )

        # Optimization Settings
        st.subheader("🔧 Optimization Settings")
        max_iterations = st.slider(
            "Max Iterations",
            min_value=5,
            max_value=30,
            value=config.get('optimization', {}).get('max_iterations', 15)
        )
        target_success_rate = st.slider(
            "Target Success Rate (%)",
            min_value=80,
            max_value=100,
            value=config.get('optimization', {}).get('target_success_rate', 100)
        )
        feedback_frequency = st.slider(
            "Feedback Frequency (iterations)",
            min_value=2,
            max_value=5,
            value=config.get('optimization', {}).get('feedback_frequency', 3)
        )

        # Performance Settings
        st.subheader("⚡ Performance Settings")
        enable_parallel = st.checkbox(
            "Enable Parallel Processing",
            value=config.get('performance', {}).get('enable_parallel', True)
        )
        max_workers = st.slider(
            "Max Workers",
            min_value=1,
            max_value=8,
            value=config.get('performance', {}).get('max_workers', 4),
            disabled=not enable_parallel
        )

        # Save configuration button
        if st.button("💾 Save Configuration", type="secondary"):
            # Update config with new values
            if 'project' not in config:
                config['project'] = {}
            config['project']['name'] = project_name
            config['project']['version'] = project_version

            if 'optimization' not in config:
                config['optimization'] = {}
            config['optimization']['max_iterations'] = max_iterations
            config['optimization']['target_success_rate'] = target_success_rate
            config['optimization']['feedback_frequency'] = feedback_frequency

            if 'performance' not in config:
                config['performance'] = {}
            config['performance']['enable_parallel'] = enable_parallel
            config['performance']['max_workers'] = max_workers

            if save_config(config):
                st.success("✅ Configuration saved successfully!")
            else:
                st.error("❌ Failed to save configuration")

    # Main content area - tabs
    tab1, tab2, tab3 = st.tabs(["📝 Setup", "🚀 Generate", "📊 Results"])

    # Tab 1: Setup
    with tab1:
        st.header("Setup Your Prompt Generation")

        # Use case input
        st.subheader("🎯 Use Case Description")
        use_case = st.text_area(
            "Describe what you want the prompt to do",
            value=config.get('project', {}).get('use_case', ''),
            height=100,
            placeholder="Example: Based on the company description classify which companies IT dependency into high, medium or low."
        )

        # Save use case to session state
        st.session_state['use_case'] = use_case

        # Data upload section
        st.subheader("📂 Golden Data")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            Upload your test data in Excel format with two columns:
            - **input_data**: The input for testing
            - **expected_output**: The expected output
            """)

        with col2:
            # Create sample data button
            if st.button("📥 Download Sample Template"):
                sample_data = {
                    'input_data': ['What is 2+2?', 'What is the capital of France?', 'Translate "hello" to Spanish'],
                    'expected_output': ['4', 'Paris', 'hola']
                }
                df_sample = pd.DataFrame(sample_data)

                # Convert to Excel bytes
                output = pd.ExcelWriter('sample_template.xlsx', engine='openpyxl')
                df_sample.to_excel(output, index=False)
                output.close()

                with open('sample_template.xlsx', 'rb') as f:
                    st.download_button(
                        label="Download Template",
                        data=f,
                        file_name="golden_data_template.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your golden data Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with 'input_data' and 'expected_output' columns"
        )

        # Load and preview data
        if uploaded_file is not None:
            data_pairs, df = load_excel_data(uploaded_file=uploaded_file)

            if data_pairs:
                # Check if reason column is present
                has_reason = any(len(pair) == 3 for pair in data_pairs)
                reason_count = sum(1 for pair in data_pairs if len(pair) == 3)

                if has_reason:
                    st.success(f"✅ Loaded {len(data_pairs)} test cases successfully! ({reason_count} with reasoning)")
                    st.info("💡 Reason column detected! This will be used to improve prompt optimization.")
                else:
                    st.success(f"✅ Loaded {len(data_pairs)} test cases successfully!")

                # Preview data
                st.subheader("📋 Data Preview")
                st.dataframe(df, use_container_width=True)

                # Save to session state
                st.session_state['test_data'] = data_pairs
                st.session_state['uploaded_file'] = uploaded_file.name
            else:
                st.error("❌ No valid test data found in the uploaded file.")
        elif os.path.exists('data/golden_data.xlsx'):
            # Try loading default file
            if st.checkbox("📁 Use existing data/golden_data.xlsx"):
                data_pairs, df = load_excel_data(file_path='data/golden_data.xlsx')
                if data_pairs:
                    # Check if reason column is present
                    has_reason = any(len(pair) == 3 for pair in data_pairs)
                    reason_count = sum(1 for pair in data_pairs if len(pair) == 3)

                    if has_reason:
                        st.success(f"✅ Loaded {len(data_pairs)} test cases from default file! ({reason_count} with reasoning)")
                        st.info("💡 Reason column detected! This will be used to improve prompt optimization.")
                    else:
                        st.success(f"✅ Loaded {len(data_pairs)} test cases from default file!")

                    st.subheader("📋 Data Preview")
                    st.dataframe(df, use_container_width=True)
                    st.session_state['test_data'] = data_pairs
                    st.session_state['uploaded_file'] = 'data/golden_data.xlsx'

    # Tab 2: Generate
    with tab2:
        st.header("Generate Golden Prompt")

        # Check if we have the required data
        if 'use_case' not in st.session_state or not st.session_state.get('use_case'):
            st.warning("⚠️ Please provide a use case description in the Setup tab.")
            return

        if 'test_data' not in st.session_state or not st.session_state.get('test_data'):
            st.warning("⚠️ Please upload golden data in the Setup tab.")
            return

        # Display current setup
        st.subheader("📋 Current Setup")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Use Case:** {st.session_state['use_case'][:100]}...")
        with col2:
            st.info(f"**Test Cases:** {len(st.session_state['test_data'])} cases loaded")

        st.markdown("---")

        # Generate button
        if st.button("🚀 Generate Golden Prompt", type="primary", use_container_width=True):
            # Create placeholder for progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.container()

            # Initialize optimizer
            try:
                with log_container:
                    st.markdown("### 📊 Generation Progress")

                    # Create progress tracking
                    progress_placeholder = st.empty()
                    log_placeholder = st.empty()

                    # Capture logs
                    logs = []

                    def log(message):
                        logs.append(message)
                        log_placeholder.text_area("Logs", "\n".join(logs[-20:]), height=300)

                    log("🔧 Initializing PromptOptimizer...")
                    optimizer = PromptOptimizer()

                    log("🚀 Starting optimization process...")

                    # Update config
                    config = load_config()
                    config['optimization']['max_iterations'] = max_iterations
                    config['optimization']['target_success_rate'] = target_success_rate
                    config['optimization']['feedback_frequency'] = feedback_frequency
                    config['performance']['enable_parallel'] = enable_parallel
                    config['performance']['max_workers'] = max_workers
                    save_config(config)

                    # Reload optimizer with new config
                    optimizer = PromptOptimizer()

                    # Generate golden prompt
                    test_data = st.session_state['test_data']
                    use_case = st.session_state['use_case']

                    # This will use the console output - we'd need to redirect stdout to capture it
                    # For now, we'll run it directly
                    golden_prompt = optimizer.create_golden_prompt(
                        use_case,
                        test_data,
                        max_iterations=max_iterations
                    )

                    progress_bar.progress(100)

                    if golden_prompt:
                        # Calculate final metrics
                        final_matches, total, final_failed = optimizer.test_prompt_with_data(
                            golden_prompt, test_data, verbose=False
                        )
                        final_quality = optimizer.calculate_quality_score(golden_prompt, test_data)

                        # Save to session state
                        st.session_state['golden_prompt'] = golden_prompt
                        st.session_state['final_quality'] = final_quality
                        st.session_state['final_failed'] = final_failed
                        st.session_state['generation_complete'] = True

                        st.success("✅ Golden prompt generated successfully!")
                        st.info("📊 Check the Results tab to view and download your prompt.")
                    else:
                        st.error("❌ Failed to generate golden prompt")

            except Exception as e:
                st.error(f"❌ Error during generation: {e}")
                import traceback
                st.code(traceback.format_exc())

    # Tab 3: Results
    with tab3:
        st.header("📊 Results")

        if 'generation_complete' not in st.session_state or not st.session_state.get('generation_complete'):
            st.info("ℹ️ Generate a golden prompt first to see results here.")
            return

        # Display metrics
        st.subheader("🎯 Performance Metrics")

        quality = st.session_state['final_quality']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Success Rate",
                value=f"{quality['success_rate']:.1f}%",
                delta="Perfect!" if quality['success_rate'] == 100 else None
            )

        with col2:
            st.metric(
                label="Quality Score",
                value=f"{quality['overall_quality']:.1f}/100"
            )

        with col3:
            st.metric(
                label="Consistency",
                value=f"{quality['consistency_score']:.1f}/100"
            )

        with col4:
            st.metric(
                label="Robustness",
                value=f"{quality['robustness_score']:.1f}/100"
            )

        st.markdown("---")

        # Display failed cases if any
        if st.session_state.get('final_failed'):
            with st.expander(f"⚠️ Failed Cases ({len(st.session_state['final_failed'])} cases)"):
                for i, case in enumerate(st.session_state['final_failed'][:5]):
                    # Handle both (input, expected, actual) and (input, expected, actual, reason)
                    if len(case) == 4:
                        inp, exp, got, reason = case
                        st.markdown(f"**Case {i+1}:**")
                        st.markdown(f"- **Input:** {inp}")
                        st.markdown(f"- **Expected:** {exp}")
                        st.markdown(f"- **Got:** {got}")
                        st.markdown(f"- **Reason:** {reason}")
                    else:
                        inp, exp, got = case
                        st.markdown(f"**Case {i+1}:**")
                        st.markdown(f"- **Input:** {inp}")
                        st.markdown(f"- **Expected:** {exp}")
                        st.markdown(f"- **Got:** {got}")
                    st.markdown("---")

        # Display golden prompt
        st.subheader("🏆 Golden Prompt")
        golden_prompt = st.session_state['golden_prompt']

        st.text_area(
            "Generated Prompt",
            value=golden_prompt,
            height=300,
            disabled=True
        )

        # Download buttons
        st.subheader("💾 Download Results")

        col1, col2 = st.columns(2)

        with col1:
            # Download prompt
            st.download_button(
                label="📄 Download Prompt (TXT)",
                data=golden_prompt,
                file_name="golden_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            # Download results JSON
            results_summary = {
                "project_name": config.get('project', {}).get('name', 'Golden Prompt Generator'),
                "project_version": config.get('project', {}).get('version', '2.0.0'),
                "use_case": st.session_state.get('use_case', ''),
                "timestamp": pd.Timestamp.now().isoformat(),
                "test_cases_count": len(st.session_state.get('test_data', [])),
                "final_success_rate": quality['success_rate'],
                "final_quality_score": quality['overall_quality'],
                "consistency_score": quality['consistency_score'],
                "robustness_score": quality['robustness_score'],
                "failed_cases_count": len(st.session_state.get('final_failed', []))
            }

            st.download_button(
                label="📊 Download Results (JSON)",
                data=json.dumps(results_summary, indent=2),
                file_name="results.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
