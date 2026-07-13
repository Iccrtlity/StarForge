# Enhanced generate-readme Command Documentation

## Overview

The enhanced `generate_readme` command automatically scans your project, detects the tech stack, and generates professional README files. It supports multiple AI providers and customizable tones.

## Features

### ✨ Automatic Project Scanning
- Recursively scans project directory
- Ignores common non-essential directories: `.git`, `node_modules`, `.venv`, `__pycache__`, etc.
- Detects tech stack automatically (Python, JavaScript, Go, Rust, Java, etc.)
- Counts lines of code and file statistics
- Extracts project description from existing README if available

### 🤖 Multi-Provider LLM Support
- **Ollama** (Local, free, privacy-first)
  - Runs completely offline
  - No API keys needed
  - Supports: mistral, neural-chat, llama2, and more
  
- **Gemini** (Google's API)
  - Requires `GOOGLE_API_KEY` environment variable
  - Best for large-scale text generation
  
- **OpenAI-Compatible** (OpenAI, Mistral, Azure, etc.)
  - Works with any OpenAI-compatible API
  - Requires `OPENAI_API_KEY` environment variable
  - Supports custom base URLs for private deployments

### 🎯 Customizable Tones
- **Viral**: Bold, engaging, emphasizes unique features
- **Professional**: Formal, comprehensive, suitable for enterprise
- **Minimal**: Concise, straight-to-the-point

### 📋 Generated README Sections
1. **Title & Badges** - Project name with technology badges
2. **Description** - Auto-generated summary of the project
3. **Features** - Key capabilities and highlights
4. **Tech Stack** - Detected technologies and frameworks
5. **Quick Start** - Installation and basic setup
6. **Usage** - Example usage and common commands
7. **Architecture** - Project structure overview
8. **Screenshots** - Placeholder for visual demos
9. **Contributing** - Contribution guidelines
10. **License** - License information
11. **Footer** - Build credits and year

## Installation

```bash
# Clone or update the repository
git clone https://github.com/yourusername/StarForge.git
cd StarForge

# Install with all providers
pip install -e .

# Or install with optional providers
pip install -e ".[dev]"  # With development dependencies
```

## Usage Examples

### Basic Preview (No LLM Required)
```bash
# Generate README preview without AI
starforge generate-readme . --skip-llm
```

### With Ollama (Local AI)
```bash
# Start Ollama server first
ollama serve

# In another terminal, generate README with Ollama
starforge generate-readme . --provider ollama --model mistral

# Use specific tone
starforge generate-readme . --provider ollama --tone viral

# Save to file
starforge generate-readme . --provider ollama --output save
```

### With Google Gemini
```bash
# Set your API key
export GOOGLE_API_KEY="your-api-key-here"

# Generate README with Gemini
starforge generate-readme . --provider gemini

# Use custom model
starforge generate-readme . --provider gemini --model gemini-pro
```

### With OpenAI or Compatible APIs
```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Generate with OpenAI
starforge generate-readme . --provider openai --model gpt-4

# Customize LLM behavior
starforge generate-readme . --provider openai --model gpt-4 \
  --max-tokens 4000 --temperature 0.7
```

### Combine Options
```bash
# Professional tone, save to file
starforge generate-readme ./my-project --tone professional --output save

# Viral tone preview
starforge generate-readme . --tone viral --output preview

# Minimal tone with Ollama
starforge generate-readme . --tone minimal --provider ollama --output save
```

## Command Line Options

```
Arguments:
  [PATH]                    Path to the project directory (default: .)

Options:
  -p, --provider TEXT       LLM provider: ollama, gemini, or openai
                            (default: ollama)
  
  -t, --tone TEXT          Tone: viral, professional, or minimal
                            (default: professional)
  
  -o, --output TEXT        Output mode: preview (print) or save (to file)
                            (default: preview)
  
  -m, --model TEXT         Specific model to use
                            Examples: mistral, gpt-4, gemini-pro
  
  --skip-llm               Generate README without LLM (template only)
  
  --help                   Show help message
```

## Environment Variables

### Ollama
No environment variables needed. Ollama runs locally on `http://localhost:11434` by default.

### Gemini
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Custom OpenAI-Compatible
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://your-api-endpoint"
```

## Implementation Details

### Project Scanner
The `ProjectScanner` class:
- Recursively scans directories
- Detects 20+ technology patterns (Python, JavaScript, TypeScript, Go, Rust, Docker, etc.)
- Counts lines of code for common programming languages
- Extracts project purpose from existing documentation
- Provides framework-specific information (dependencies, package names, etc.)

### LLM Providers
All providers implement the `LLMProvider` abstract base class:
- **Lazy initialization** of clients
- **Error handling** with meaningful messages
- **Fallback support** when providers unavailable
- **Consistent interface** across all backends

### Prompt Templates
Customizable prompt templates for different tones:
- **Viral**: Engaging, benefit-focused language
- **Professional**: Formal, comprehensive documentation style
- **Minimal**: Concise, direct information delivery

### README Generator
The `ReadmeGenerator` class:
- Coordinates project scanning and LLM generation
- Generates structured markdown with proper formatting
- Includes badges with technology colors
- Creates fallback content when LLM unavailable
- Validates all inputs and provides clear error messages

## Error Handling

The command includes comprehensive error handling:
- Invalid tone/output/provider options with helpful suggestions
- LLM provider availability checks before generation
- Graceful fallback to template-based generation
- Clear error messages for troubleshooting
- Support for `--debug` flag for detailed error traces

### Common Issues

**Ollama not available**
```
⚠️ Ollama is not available at http://localhost:11434. 
Make sure Ollama is running with: ollama serve
```
Solution: Start Ollama or use `--skip-llm` flag

**API key not configured**
```
✗ Gemini API key not configured. 
Set GOOGLE_API_KEY environment variable.
```
Solution: Set the appropriate environment variable

**Invalid tone**
```
✗ Invalid tone: something
Valid tones: viral, professional, minimal
```
Solution: Use one of the valid tone options

## Best Practices

### For Best Results
1. **Add an existing README** - Scanner will extract description from it
2. **Organize your project** - Proper structure helps tech detection
3. **Use meaningful filenames** - Aids in project understanding
4. **Choose appropriate tone**:
   - Use "viral" for open-source projects seeking adoption
   - Use "professional" for enterprise/serious projects
   - Use "minimal" for internal tools or minimal docs

### Privacy & Performance
- **Local-first**: Use Ollama for complete privacy
- **Performance**: Gemini and OpenAI are faster for large generation
- **Cost**: Ollama is free (no API calls), others have per-token pricing

## Extending the System

### Adding New Providers
Create a new class inheriting from `LLMProvider`:

```python
from starforge.providers import LLMProvider

class MyProvider(LLMProvider):
    def is_available(self) -> bool:
        # Check if available
        pass
    
    def generate(self, prompt: str, system_prompt=None) -> str:
        # Generate text using your API
        pass
```

### Custom Tones
Add new tones in `starforge/prompts.py`:

```python
SYSTEM_PROMPTS = {
    "my_tone": "Your custom system prompt here...",
}
```

## Testing

Test the enhanced command:

```bash
# Test with skip-llm (no API calls needed)
starforge generate-readme . --skip-llm --output preview

# Test with different tones
starforge generate-readme . --skip-llm --tone viral
starforge generate-readme . --skip-llm --tone minimal

# Test help
starforge generate-readme --help
```

## Performance Considerations

- **Scanning**: ~100-500ms depending on project size
- **Generation**: 
  - Ollama: 5-30 seconds depending on model and complexity
  - Gemini: 2-10 seconds
  - OpenAI: 2-10 seconds
- **File I/O**: <100ms

## Troubleshooting

Run with verbose output:
```bash
starforge generate-readme . --debug
```

Check logs for detailed error information and trace information.

## Future Enhancements

Potential additions:
- [ ] Interactive CLI mode for configuration
- [ ] README templates customization
- [ ] Multi-language support
- [ ] Table of contents generation
- [ ] Automatic screenshot placeholder sizing
- [ ] Integration with GitHub API for star/fork history
- [ ] Social media post generation
