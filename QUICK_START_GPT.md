# Quick Start: Using GPT with PromptForge

This guide shows how to quickly get started with GPT (OpenAI) models.

## Prerequisites

- PromptForge installed
- OpenAI API key (get from https://platform.openai.com/api-keys)

## Setup (3 Steps)

### 1. Install OpenAI Support

```bash
pip install -e ".[gpt]"
```

Or just install the OpenAI library:
```bash
pip install openai
```

### 2. Add API Key

Create or edit `.env` file:
```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 3. Update config.yml

Change the provider from `claude` to `gpt`:

```yaml
models:
  initial_prompt_generator:
    provider: gpt              # Changed from 'claude'
    model: gpt-4o             # Changed from claude model
    temperature: 0.7
  
  answer_generator:
    provider: gpt
    model: gpt-4o-mini        # Fast, cost-effective
    temperature: 0.3
  
  prompt_optimizer:
    provider: gpt
    model: gpt-4o
    temperature: 0.5
```

## Run It!

```bash
# Using CLI
python main.py

# Using Web Interface
streamlit run app.py

# Run predictions
python predict.py
```

## Model Options

| Model | Use Case | Cost |
|-------|----------|------|
| `gpt-4o` | Best quality, complex tasks | $$$ |
| `gpt-4o-mini` | Fast, cost-effective | $ |
| `gpt-4-turbo` | Balanced performance | $$ |
| `gpt-4` | Previous generation | $$ |
| `gpt-3.5-turbo` | Budget option | $ |

## Example Configurations

### Pure GPT (All Stages)

```yaml
models:
  initial_prompt_generator:
    provider: gpt
    model: gpt-4o
  answer_generator:
    provider: gpt
    model: gpt-4o-mini
  prompt_optimizer:
    provider: gpt
    model: gpt-4o
  feedback_collector:
    provider: gpt
    model: gpt-4o
  prompt_evolver:
    provider: gpt
    model: gpt-4o
```

### Mixed (Claude + GPT)

```yaml
models:
  # Use Claude for sophisticated prompt generation
  initial_prompt_generator:
    provider: claude
    model: claude-sonnet-4-5-20250929
  
  # Use GPT for fast, cost-effective testing
  answer_generator:
    provider: gpt
    model: gpt-4o-mini
  
  # Use Claude for optimization
  prompt_optimizer:
    provider: claude
    model: claude-sonnet-4-5-20250929
```

## Troubleshooting

### "OpenAI library not installed"
```bash
pip install openai
```

### "OPENAI_API_KEY not found"
Check your `.env` file:
```bash
cat .env | grep OPENAI
```

Should show:
```
OPENAI_API_KEY=sk-...
```

### "Model not found"
Make sure you're using a valid GPT model name:
- ✅ `gpt-4o`
- ✅ `gpt-4o-mini`
- ✅ `gpt-4-turbo`
- ❌ `gpt-5` (doesn't exist yet)

## Testing

Test the GPT connection:
```bash
python utils/llms.py
```

You should see:
```
✅ GPT response: 2 + 2 = 4...
```

## Next Steps

1. Try generating a golden prompt with GPT
2. Compare Claude vs GPT performance
3. Experiment with mixed providers
4. Use gpt-4o-mini for faster/cheaper predictions

## Full Example Config

See `config.gpt.example.yml` for a complete configuration example.

## Support

- GitHub Issues: https://github.com/Hemanthkaruturi/PromptForge/issues
- Documentation: README.md
- Examples: config.gpt.example.yml

---

**Happy Prompting with GPT!** 🚀
