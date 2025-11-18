# Deployment Guide

This guide explains how to deploy and use the Browser-Based Automated Testing Builder.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for Playwright browser downloads)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/agileandy/testTool.git
cd testTool
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the Package

```bash
pip install -e .
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
# Optional: Install additional browsers
playwright install firefox
playwright install webkit
```

## Verification

Test the installation:

```bash
testtool --version
testtool --help
```

## Quick Start

### 1. Run Example Tests

```bash
# Execute an example (headless mode)
testtool execute examples/basic_navigation --headless

# Execute with visible browser
testtool execute examples/basic_navigation --headed
```

### 2. Create Your First Test

```bash
# Start interactive recording
testtool record --name my_first_test --description "My first test" --mode dumb

# Follow the prompts to enter commands:
# > go to https://example.com
# > click h1
# > screenshot
# > done
```

### 3. Execute Your Test

```bash
testtool execute my_first_test --headless
```

## Configuration

### Environment Variables

Optional environment variables for advanced features:

```bash
# For LLM-based natural language interpretation
export OPENAI_API_KEY="your-openai-api-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Directory Structure

The tool creates these directories on first use:

```
./test_scripts/       # Your saved test scripts
./screenshots/        # Screenshots from executions
./test_results/       # Execution result logs
./knowledge_base/     # Learned patterns and mappings
```

## Usage Modes

### Dumb Mode (Default)

No access to application source code. Relies on:
- Natural language instructions
- Visible browser behavior
- Generic selectors

**Best for:**
- Testing third-party applications
- Black-box testing
- When source code is unavailable

### Smart Mode

Analyzes application source code to extract:
- data-testid attributes
- Component structure
- Routes and API endpoints

**Best for:**
- Testing your own applications
- White-box testing
- Automated test generation

**Usage:**
```bash
# First, analyze the source
testtool analyze /path/to/app/source --output analysis.json

# Then create tests in smart mode
testtool record --name smart_test --description "Smart mode test" --mode smart
```

## Common Commands

### Recording Tests

```bash
# Interactive recording
testtool record --name test_name --description "Description" [--mode dumb|smart]
```

### Executing Tests

```bash
# Headless execution (default)
testtool execute test_name

# Headed execution (see browser)
testtool execute test_name --headed

# Execute with YAML format
testtool execute test_name --format yaml
```

### Managing Tests

```bash
# List all test scripts
testtool list-scripts

# Interpret natural language
testtool interpret "click the login button"

# View learned patterns
testtool patterns

# View knowledge base
testtool knowledge
```

### Exploration Mode

```bash
# Interactively explore a website
testtool explore https://example.com --headed

# Available commands in exploration:
# - click <selector>
# - type <selector> <text>
# - screenshot
# - done
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Browser Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -e .
          playwright install chromium
      
      - name: Run tests
        run: |
          testtool execute test_suite --headless
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -e .'
                sh 'playwright install chromium'
            }
        }
        
        stage('Test') {
            steps {
                sh 'testtool execute test_suite --headless'
            }
        }
    }
}
```

## Programmatic Usage

### Python API

```python
import asyncio
from testTool.models.action import Action, ActionType
from testTool.models.test_script import TestScript, TestStep
from testTool.executor import TestExecutor
from testTool.recorder import ScriptStorage

# Create a test programmatically
script = TestScript(
    name="api_test",
    description="Test via API",
    steps=[
        TestStep(
            description="Navigate",
            action=Action(type=ActionType.NAVIGATE, value="https://example.com")
        )
    ]
)

# Save it
storage = ScriptStorage()
storage.save(script)

# Execute it
executor = TestExecutor(headless=True)
result = executor.execute_sync(script)

print(f"Test {'passed' if result.success else 'failed'}")
```

## Troubleshooting

### Browser Not Found

```bash
# Install Playwright browsers
playwright install chromium
```

### Permission Errors

```bash
# On Linux, you may need to install additional dependencies
sudo apt-get install -y libgbm1 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
```

### Headless Mode Issues

If headless mode fails, try headed mode for debugging:

```bash
testtool execute test_name --headed
```

### Selector Not Found

- Increase timeout in action definition
- Use more specific selectors
- Check element is visible and interactable
- Use `data-testid` attributes in your app (Smart Mode)

## Performance Optimization

### Parallel Execution (Future)

Currently, tests execute sequentially. Parallel execution is planned.

### Reusing Browser Context

For multiple tests, consider programmatic API to reuse browser instances.

### Caching

The knowledge base and learned patterns are automatically cached between runs.

## Security Considerations

### Credentials

Never store credentials in test scripts. Use environment variables:

```bash
export TEST_USERNAME="user"
export TEST_PASSWORD="pass"
```

Access in tests via environment variable substitution (future feature).

### Screenshots

Screenshots may contain sensitive data. Ensure they're not committed to version control:

```bash
# Add to .gitignore
screenshots/
test_results/
```

## Upgrading

```bash
# Pull latest changes
git pull origin main

# Reinstall package
pip install -e . --upgrade

# Update Playwright browsers
playwright install chromium --force
```

## Support

For issues or questions:
1. Check the README.md for documentation
2. Review ARCHITECTURE.md for technical details
3. Examine example test scripts in `examples/`
4. Check test cases in `tests/` for usage patterns

## Best Practices

1. **Use Descriptive Names**: Name tests and steps clearly
2. **Add Expected Outcomes**: Document what each step should achieve
3. **Prefer Stable Selectors**: Use `data-testid` attributes when possible
4. **Version Control**: Store test scripts in git
5. **Regular Cleanup**: Remove obsolete tests
6. **Learn from Patterns**: Review learned patterns periodically
7. **Document Tests**: Add metadata and tags to scripts
8. **Incremental Testing**: Start with simple tests, build complexity

## Next Steps

1. Create your first test
2. Set up CI/CD integration
3. Analyze your application source (Smart Mode)
4. Build a comprehensive test suite
5. Monitor and maintain learned patterns
