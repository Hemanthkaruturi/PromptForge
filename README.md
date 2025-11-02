# PromptForge - Advanced Golden Prompt Generator

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)](https://claude.ai)

**PromptForge** is an intelligent prompt optimization system that automatically generates, tests, and refines prompts to achieve maximum accuracy and consistency. Using advanced feedback loops, multi-model architectures, and comprehensive quality analytics, PromptForge creates "golden prompts" that consistently deliver the desired outputs.

## Key Features

### **Intelligent Optimization**
- **Iterative Refinement**: Systematically improves prompts through multiple optimization cycles
- **Feedback-Driven Evolution**: Uses comprehensive failure analysis to evolve prompts
- **Quality Scoring**: Multi-dimensional evaluation beyond simple accuracy metrics

### **Multi-Model Architecture**
- **Flexible Model Selection**: Use different models for generation vs testing
- **Stage-Specific Optimization**: Different models for different optimization stages
- **Production Testing**: Generate with high-end models, test with production models

### **Data-Driven Approach**
- **Excel Integration**: Load test cases from Excel files with flexible column mapping
- **Comprehensive Testing**: Test against entire datasets, not just single examples
- **Performance Analytics**: Detailed metrics and failure pattern analysis

### **Advanced Configuration**
- **YAML Configuration**: Complete control through `config.yml`
- **Reproducible Results**: Consistent optimization with saved configurations
- **Professional Deployment**: Production-ready configuration management

### **High-Performance Processing**
- **Parallel Execution**: Concurrent test processing for 3-10x speed improvements
- **Intelligent Batching**: Smart batch processing with configurable worker pools
- **Rate Limiting**: API-safe concurrent requests with exponential backoff
- **Auto-Fallback**: Graceful degradation to sequential processing when needed

### **Professional File Management**
- **Organized Storage**: Automated `golden_prompts/` folder organization
- **Smart Naming**: Project name, version, and timestamp-based file naming
- **Rich Metadata**: Comprehensive performance metrics and configuration tracking
- **JSON Results**: Structured optimization results with detailed analytics

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prompt_generator
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -e .
   ```

3. **Set up your API key**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   # or create a .env file
   echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
   ```

### Basic Usage

1. **Prepare your test data**
   - Create an Excel file with `input_data` and `expected_output` columns
   - Place it in `data/golden_data.xlsx`

2. **Configure your optimization**
   ```yaml
   # config.yml
   project:
     use_case: "Your task description here"

   optimization:
     max_iterations: 15
     target_success_rate: 100
   ```

3. **Run the optimization**
   ```bash
   python main.py
   ```

### Using the Streamlit Web Interface

For a more interactive experience, you can use the Streamlit web interface:

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**
   - The app will automatically open in your browser at `http://localhost:8501`
   - Or navigate to the URL shown in the terminal

3. **Using the interface**

   **Setup Tab (📝):**
   - Enter your use case description
   - Upload your golden data Excel file
   - Preview your test data
   - Download a sample template if needed

   **Generate Tab (🚀):**
   - Review your setup
   - Click "Generate Golden Prompt" to start optimization
   - Monitor real-time progress

   **Results Tab (📊):**
   - View performance metrics (success rate, quality scores)
   - Review failed test cases
   - Download the generated prompt (TXT)
   - Download optimization results (JSON)

4. **Configuration (⚙️ Sidebar):**
   - Adjust optimization settings (max iterations, target success rate)
   - Configure performance settings (parallel processing, workers)
   - Save configuration changes

### Command Line vs Web Interface

**Use `python main.py` when:**
- Running in automated pipelines
- Prefer command-line workflows
- Need to integrate with other scripts
- Running on headless servers

**Use `streamlit run app.py` when:**
- Want visual feedback and progress tracking
- Need to quickly adjust parameters
- Prefer GUI over command line
- Want to experiment with different configurations
- Need to share with non-technical users

Both methods:
- Use the same underlying optimization engine
- Support all configuration options
- Generate identical results
- Can be run independently

## Configuration Guide

### Model Configuration
Configure different models for different optimization stages:

```yaml
models:
  # High-end model for generating initial prompts
  initial_prompt_generator:
    model: "claude-sonnet-4-5-20250929"
    temperature: 0.7

  # Production model for testing prompts
  answer_generator:
    model: "claude-haiku-4-5-20251001"
    temperature: 0.3

  # High-end model for optimization
  prompt_optimizer:
    model: "claude-sonnet-4-5-20250929"
    temperature: 0.5
```

### Optimization Settings
Control the optimization process:

```yaml
optimization:
  max_iterations: 15              # Maximum optimization cycles
  target_success_rate: 100        # Stop early if achieved
  feedback_frequency: 3           # Comprehensive feedback every N iterations
  min_quality_threshold: 85       # Minimum quality to consider "good"
```

### Data Configuration
Customize data loading and validation:

```yaml
data:
  excel_file: "data/golden_data.xlsx"
  input_column: "input_data"
  output_column: "expected_output"
  max_test_cases: 100            # Limit test cases (0 = no limit)
  skip_empty_rows: true
```

### Performance Configuration
Configure parallel processing and performance optimization:

```yaml
performance:
  # Parallel processing for faster execution
  enable_parallel: true
  max_workers: 4                      # Number of concurrent workers
  batch_size: 8                       # Process test cases in batches

  # Rate limiting for API calls
  api_rate_limit: 60                  # requests per minute
  rate_limit_delay: 1.0               # seconds between API calls

  # Retry settings for failed API calls
  max_retries: 3
  retry_delay: 2                      # seconds
  exponential_backoff: true           # Increase delay exponentially
```

## Architecture

### Core Components

#### **PromptOptimizer** (`prompt_optimizer.py`)
The heart of the system containing:
- **Initial Prompt Generation**: Creates sophisticated starting prompts
- **Iterative Optimization**: Refines prompts based on failures
- **Feedback Collection**: Analyzes performance patterns
- **Prompt Evolution**: Systematic improvement based on comprehensive feedback

#### **Main Workflow** (`main.py`)
- Configuration loading and validation
- Data management and Excel integration
- Results processing and file output
- User interface and progress reporting

#### **Advanced Prompts** (`prompts/prompts.yml`)
Sophisticated prompt templates for:
- **INITIAL_PROMPT_GENERATOR**: Creates high-quality initial prompts
- **PROMPT_OPTIMIZER**: Targeted optimization for specific failures
- **FEEDBACK_COLLECTOR**: Comprehensive performance analysis
- **PROMPT_EVOLVER**: Systematic evolution based on patterns

### System Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        A[config.yml]
        B[Excel Test Data]
        C[Use Case]
    end

    subgraph "PromptOptimizer Core"
        D[Configuration Loader]
        E[Data Validator]
        F[Initial Prompt Generator]
        G[Answer Generator]
        H[Quality Scorer]
        I[Feedback Collector]
        J[Prompt Evolver]
        K[Optimization Engine]
    end

    subgraph "Model Layer"
        L[Claude Sonnet 4<br/>Initial Generation]
        M[Claude Haiku 4<br/>Answer Testing]
        N[Claude Sonnet 4<br/>Optimization]
        O[Claude Sonnet 4<br/>Feedback Analysis]
    end

    subgraph "Output Layer"
        P[Golden Prompt]
        Q[Quality Metrics]
        R[Optimization Results]
    end

    A --> D
    B --> E
    C --> F
    D --> K
    E --> K
    F --> L
    L --> G
    G --> M
    M --> H
    H --> I
    I --> O
    O --> J
    J --> N
    N --> K
    K --> P
    K --> Q
    K --> R

    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style P fill:#c8e6c9
    style Q fill:#c8e6c9
    style R fill:#c8e6c9
    style K fill:#fff3e0
```

### Optimization Process Flow

```mermaid
flowchart TD
    START([Start Optimization]) --> LOAD[Load Configuration & Data]
    LOAD --> INIT[Generate Initial Prompt<br/>using High-End Model]
    INIT --> TEST[Test Prompt Against<br/>All Test Cases]
    TEST --> SCORE[Calculate Quality Metrics<br/>Success Rate, Consistency, etc.]

    SCORE --> TARGET{Target<br/>Achieved?}
    TARGET -->|Yes| SAVE[Save Golden Prompt<br/>with Metadata]
    TARGET -->|No| MAXITER{Max Iterations<br/>Reached?}

    MAXITER -->|Yes| SAVE
    MAXITER -->|No| FEEDBACK{Feedback<br/>Cycle?}

    FEEDBACK -->|Yes| COLLECT[Collect Comprehensive<br/>Feedback & Patterns]
    COLLECT --> EVOLVE[Evolve Prompt using<br/>Strategic Analysis]
    EVOLVE --> TEST

    FEEDBACK -->|No| OPTIMIZE[Quick Optimization<br/>based on Failed Case]
    OPTIMIZE --> TEST

    SAVE --> END([End - Golden Prompt Ready])

    style START fill:#c8e6c9
    style END fill:#c8e6c9
    style TARGET fill:#fff3e0
    style FEEDBACK fill:#fff3e0
    style MAXITER fill:#fff3e0
    style SAVE fill:#ffecb3
```

### Multi-Model Architecture

```mermaid
graph LR
    subgraph "Generation Stage"
        A[Use Case + Sample Data] --> B[Claude Sonnet 4<br/>Initial Prompt Generator]
        B --> C[Sophisticated<br/>Initial Prompt]
    end

    subgraph "Testing Stage"
        C --> D[Claude Haiku 4<br/>Answer Generator]
        D --> E[Generated Responses]
        E --> F[Quality Assessment]
    end

    subgraph "Optimization Stage"
        F --> G{Performance<br/>Issues?}
        G -->|Failed Cases| H[Claude Sonnet 4<br/>Prompt Optimizer]
        G -->|Pattern Issues| I[Claude Sonnet 4<br/>Feedback Collector]
        I --> J[Claude Sonnet 4<br/>Prompt Evolver]
        H --> C
        J --> C
    end

    style B fill:#ff9800
    style D fill:#4caf50
    style H fill:#ff9800
    style I fill:#ff9800
    style J fill:#ff9800
```

## Advanced Features

### Multi-Model Testing
Generate prompts with powerful models, test with production models:
```yaml
models:
  initial_prompt_generator:
    model: "claude-sonnet-4-5-20250929"  # Best for generation
  answer_generator:
    model: "claude-haiku-4-5-20251001"   # Test on faster model
```

### Quality Metrics
Beyond simple accuracy:
- **Success Rate**: Percentage of correct outputs
- **Consistency Score**: Reliability across similar inputs
- **Robustness Score**: Performance on edge cases
- **Overall Quality**: Composite score

### Feedback Loops
Systematic improvement through:
- **Immediate Optimization**: Fix specific failures quickly
- **Pattern Analysis**: Identify systematic issues every N iterations
- **Comprehensive Evolution**: Strategic prompt improvement

## Project Structure

```
prompt_generator/
├── main.py                              # Main CLI application entry point
├── app.py                               # 🆕 Streamlit web interface
├── prompt_optimizer.py                  # Core optimization engine
├── config.yml                           # Configuration file
├── golden_prompts/                      # Generated prompts storage
│   ├── PromptForge_v2.0.0_sentiment_20241102_143052.txt
│   ├── PromptForge_v2.0.0_sentiment_20241102_143052_results.json
│   └── ...                             # Organized by project, version, timestamp
├── prompts/
│   └── prompts.yml                      # Advanced prompt templates
├── utils/
│   └── llms.py                         # LLM integration utilities
├── data/
│   └── golden_data.xlsx                # Test data (Excel format)
├── pyproject.toml                      # Python dependencies
├── golden_prompt.txt                   # Latest prompt (backward compatibility)
└── README.md                           # This file
```

## Usage Examples

### Example 1: Sentiment Classification
```yaml
project:
  use_case: "Classify sentiment as positive, negative, or neutral"

data:
  excel_file: "data/sentiment_data.xlsx"

optimization:
  max_iterations: 10
  target_success_rate: 95
```

### Example 2: Data Extraction
```yaml
project:
  use_case: "Extract company name and industry from business descriptions"

models:
  initial_prompt_generator:
    model: "claude-sonnet-4-5-20250929"
  answer_generator:
    model: "claude-haiku-4-5-20251001"  # Test on faster model

optimization:
  max_iterations: 20
  feedback_frequency: 2
```

### Example 3: Code Generation
```yaml
project:
  use_case: "Generate Python functions based on natural language descriptions"

matching:
  method: "fuzzy"              # Allow slight variations
  fuzzy_threshold: 0.9

optimization:
  max_iterations: 25
  min_quality_threshold: 90
```

## Testing the Core Engine

Test the optimization engine directly:

```bash
python prompt_optimizer.py
```

This launches an interactive mode where you can:
- Enter your use case
- Add test cases manually
- See the optimization process in detail

## Output Files

### Generated Files
- **`golden_prompt.txt`**: The final optimized prompt
- **`golden_prompt_YYYYMMDD_HHMMSS.txt`**: Timestamped version with metadata
- **`optimization_results.json`**: Detailed optimization metrics (if configured)

### Metadata Included
- Generation timestamp
- Use case description
- Test case count
- Final success rate and quality scores
- Configuration used

## Troubleshooting

### Common Issues

**Configuration not loading:**
```
⚠️  Config file config.yml not found. Using defaults.
```
- Ensure `config.yml` exists in the project root
- Check YAML syntax with a validator

**Excel file issues:**
```
❌ Error loading Excel file: [Errno 2] No such file or directory
```
- Verify the Excel file path in config
- Ensure file has correct column names

**API key issues:**
```
Error: API key not found
```
- Set `ANTHROPIC_API_KEY` environment variable
- Or create a `.env` file with the key

### Performance Tips

1. **Use appropriate models**: High-end for generation, efficient for testing
2. **Limit test cases**: Start with smaller datasets for faster iteration
3. **Adjust feedback frequency**: More frequent feedback = slower but better optimization
4. **Set realistic targets**: 100% success rate might not always be achievable

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Claude](https://claude.ai) AI assistance
- Powered by [Anthropic's APIs](https://www.anthropic.com)
- Excel integration via [pandas](https://pandas.pydata.org) and [openpyxl](https://openpyxl.readthedocs.io)

---

**PromptForge** - *Forging perfect prompts through intelligent optimization*