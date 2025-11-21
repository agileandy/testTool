# Browser-Based Automated Testing Builder

A deterministic browser-driven testing tool that executes natural-language test instructions and builds reusable regression suites.

This is one of two different ideas I'm working on to build 'intelligent' AI based testing tools. The other is https://github.com/agileandy/AutoTest. Both are very much early WIP at the moment.
## Features

### Core Capabilities

- **Browser Control**: Real browser automation using Playwright (Chromium, Firefox, WebKit)
- **Natural Language Processing**: Convert human instructions to structured test actions
- **Deterministic Testing**: Same test script always produces the same execution sequence
- **Test Recording**: Capture interactions and build regression suites
- **Learning Layer**: Automatically identify common patterns and workflows
- **Dual Modes**: Dumb Mode (no source access) and Smart Mode (full source analysis)

### Key Components

1. **Browser Control Layer** - Playwright-based browser automation
2. **Natural Language Interpreter** - Converts instructions to actions
3. **Test Recorder** - Records interactions as deterministic scripts
4. **Test Executor** - Replays tests with consistent results
5. **Learning Engine** - Identifies patterns and auto-generates tests
6. **Knowledge Base** - Stores element mappings and application structure

## Installation

```bash
# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### 1. Record a Test (Interactive)

```bash
testtool record --name "login_test" --description "Test user login flow" --mode dumb
```

This starts an interactive session where you can enter commands like:
- `go to https://example.com`
- `click the login button`
- `type 'admin' in username field`
- `type 'password123' in password field`
- `click submit button`
- `done`

### 2. Execute a Test

```bash
testtool execute login_test --headless
```

### 3. List Available Tests

```bash
testtool list-scripts
```

### 4. Analyze Application (Smart Mode)

```bash
testtool analyze ./path/to/source --output analysis.json
```

### 5. View Learned Patterns

```bash
testtool patterns
```

### 6. Interactive Exploration

```bash
testtool explore https://example.com --headed
```

## Operating Modes

### Dumb Mode (No Source Access)

In Dumb Mode, the tool relies entirely on:
- Natural language instructions from humans
- Visible browser behavior
- Rule-based selector generation

**Usage:**
```bash
testtool record --name "my_test" --description "Description" --mode dumb
```

**Best Practices:**
- Provide explicit, literal instructions
- Use specific element descriptions
- Don't assume application knowledge

### Smart Mode (Full Source Access)

In Smart Mode, the tool can:
- Analyze application source code
- Extract data-testid attributes
- Discover routes and API endpoints
- Map components to selectors
- Auto-generate tests

**Usage:**
```bash
# Analyze source first
testtool analyze ./app-source --output analysis.json

# Record with smart mode
testtool record --name "smart_test" --description "Smart mode test" --mode smart
```

## Test Script Format

Tests are stored in JSON or YAML format:

```json
{
  "name": "login_test",
  "description": "Test user login flow",
  "mode": "dumb",
  "steps": [
    {
      "description": "Navigate to login page",
      "action": {
        "type": "navigate",
        "value": "https://example.com/login"
      }
    },
    {
      "description": "Enter username",
      "action": {
        "type": "type",
        "selector": "input[name='username']",
        "value": "admin"
      }
    }
  ]
}
```

## Action Types

The tool supports these action types:

- `navigate` - Navigate to a URL
- `click` - Click an element
- `type` - Type text into an input
- `select` - Select dropdown option
- `wait` - Wait for load/networkidle
- `scroll` - Scroll to element
- `screenshot` - Capture screenshot
- `assert_text` - Verify element text
- `assert_element` - Verify element exists
- `extract` - Extract text from element

## Determinism

The tool ensures deterministic execution through:

1. **Stable Selectors**: Prefers `data-testid` over fragile CSS selectors
2. **Explicit Waits**: Waits for DOM states before actions
3. **Fixed Viewport**: Consistent browser window size (1280x720)
4. **No Race Conditions**: Proper state checking before actions
5. **Filtered Snapshots**: Removes timestamps and random IDs

## Architecture

```
testTool/
├── browser_control/       # Playwright browser automation
├── nl_processor/          # Natural language interpretation
├── recorder/              # Test recording and storage
├── executor/              # Test execution engine
├── learning_layer/        # Pattern learning and knowledge base
├── models/                # Data models (Action, TestScript, etc.)
└── utils/                 # Source code analyzer and helpers
```

## CLI Commands

### `record`
Record a new test script interactively.

```bash
testtool record --name NAME --description DESC [--mode dumb|smart] [--interactive]
```

### `execute`
Execute a saved test script.

```bash
testtool execute SCRIPT_NAME [--headless] [--format json|yaml]
```

### `list-scripts`
List all available test scripts.

```bash
testtool list-scripts
```

### `interpret`
Test natural language interpretation.

```bash
testtool interpret "click the login button" [--use-llm]
```

### `analyze`
Analyze application source code (Smart Mode).

```bash
testtool analyze SOURCE_DIR [--output FILE]
```

### `patterns`
Show learned workflow patterns.

```bash
testtool patterns
```

### `knowledge`
Display knowledge base contents.

```bash
testtool knowledge
```

### `explore`
Interactively explore a website.

```bash
testtool explore URL [--headless]
```

## Advanced Usage

### Using LLM for Interpretation

Set API keys in environment:
```bash
export OPENAI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

Then enable LLM interpretation:
```python
from testTool.nl_processor import NLInterpreter

interpreter = NLInterpreter(use_llm=True, llm_provider="openai")
actions = interpreter.interpret("log in as admin with password secret123")
```

### Programmatic Usage

```python
import asyncio
from testTool.models.action import Action, ActionType
from testTool.models.test_script import TestScript, TestStep
from testTool.executor import TestExecutor

# Create a test script
script = TestScript(
    name="example_test",
    description="Example programmatic test",
    mode="dumb",
    steps=[
        TestStep(
            description="Go to homepage",
            action=Action(type=ActionType.NAVIGATE, value="https://example.com")
        ),
        TestStep(
            description="Click button",
            action=Action(type=ActionType.CLICK, selector="button#submit")
        )
    ]
)

# Execute
executor = TestExecutor(headless=True)
result = executor.execute_sync(script)

print(f"Success: {result.success}")
print(f"Duration: {result.total_duration_ms}ms")
```

### Learning from Executions

```python
from testTool.learning_layer import PatternLearner
from testTool.recorder import ScriptStorage

# Load and observe scripts
storage = ScriptStorage()
learner = PatternLearner()

for script_name in storage.list_scripts():
    script = storage.load(script_name)
    learner.observe_script(script)

# Get common patterns
patterns = learner.get_common_patterns(min_count=2)
for pattern in patterns:
    print(f"Pattern: {pattern['pattern']}")
    print(f"Seen {pattern['count']} times")
```

## Extensibility

The tool is designed to be modular and extensible:

- **Custom Actions**: Add new action types by extending `ActionType`
- **Custom Interpreters**: Implement additional NL interpretation strategies
- **Storage Backends**: Add support for databases or cloud storage
- **Reporters**: Create custom execution result formatters
- **Analyzers**: Build domain-specific source code analyzers

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=testTool --cov-report=html
```

## Directory Structure

When running the tool, it creates:

```
./test_scripts/       # Saved test scripts (JSON/YAML)
./screenshots/        # Screenshots from test execution
./test_results/       # Execution result logs
./knowledge_base/     # Learned patterns and mappings
```

## Requirements

- Python 3.8+
- Playwright
- Pydantic
- PyYAML
- Click
- Rich

## License

This project is part of the testTool repository.

## Contributing

The tool is designed to be self-contained and modular. All components are fully working and can be extended as needed.

## Support

For issues or questions, please refer to the repository documentation.
