# Usage Guide

Comprehensive guide for using the Browser-Based Automated Testing Builder.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Natural Language Commands](#natural-language-commands)
3. [Test Script Structure](#test-script-structure)
4. [Operating Modes](#operating-modes)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)

## Getting Started

### Your First Test

Create a simple navigation test:

```bash
testtool record --name homepage_test --description "Test homepage loads"
```

When prompted, enter these commands:
```
Step 1: go to https://example.com
Step 2: wait for page to load
Step 3: screenshot
Step 4: done
```

Execute your test:
```bash
testtool execute homepage_test
```

## Natural Language Commands

The tool understands these natural language patterns:

### Navigation

```
go to https://example.com
navigate to https://example.com
open https://example.com
visit https://example.com
```

### Clicking

```
click the login button
press the submit button
tap on the menu icon
click button#login
```

### Typing

```
type 'username' in the username field
enter 'password' in password
input 'text' in search box
fill 'value' in input
```

### Selecting

```
select 'option' from dropdown
choose 'value' in select
```

### Waiting

```
wait for page to load
wait for network to idle
wait 5000  (wait 5 seconds)
```

### Screenshots

```
take a screenshot
capture screen
screenshot
```

### Assertions

```
verify text 'Welcome' is present
check element h1 exists
assert text 'Success' in .message
```

### Extraction

```
extract text from h1
get text from .title
```

## Test Script Structure

### JSON Format

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
        "value": "https://example.com/login",
        "timeout": 30000
      },
      "expected_outcome": "Login page loads",
      "screenshot": false
    },
    {
      "description": "Enter username",
      "action": {
        "type": "type",
        "selector": "input[name='username']",
        "value": "testuser",
        "timeout": 30000
      },
      "expected_outcome": "Username is entered",
      "screenshot": false
    }
  ],
  "metadata": {
    "tags": ["authentication", "critical"],
    "author": "test-team"
  }
}
```

### YAML Format

```yaml
name: login_test
description: Test user login flow
mode: dumb
steps:
  - description: Navigate to login page
    action:
      type: navigate
      value: https://example.com/login
      timeout: 30000
    expected_outcome: Login page loads
    screenshot: false
    
  - description: Enter username
    action:
      type: type
      selector: input[name='username']
      value: testuser
      timeout: 30000
    expected_outcome: Username is entered
    screenshot: false

metadata:
  tags:
    - authentication
    - critical
  author: test-team
```

## Operating Modes

### Dumb Mode

Used when you don't have access to application source code.

**Characteristics:**
- Relies on visible elements
- Uses generic selectors
- Requires explicit instructions
- Works with any website

**Example:**
```bash
testtool record --name test --description "Test" --mode dumb
```

**Commands you'll use:**
```
> go to https://example.com
> click button:has-text('Login')
> type 'user@example.com' in input[type='email']
> wait for page to load
> screenshot
```

### Smart Mode

Used when you have access to application source code.

**Characteristics:**
- Analyzes source code
- Uses data-testid attributes
- Understands component structure
- Can auto-generate tests

**Setup:**
```bash
# Analyze your application source
testtool analyze ./my-app/src --output analysis.json

# View extracted information
testtool knowledge
```

**Benefits:**
- More stable selectors
- Better understanding of workflows
- Can suggest test scenarios
- Faster test creation

**Example:**
```bash
testtool record --name test --description "Test" --mode smart
```

The tool will suggest:
- Available routes
- Known components
- Common workflows

## Advanced Features

### Pattern Learning

The tool learns from your tests and identifies common patterns.

```bash
# View learned patterns
testtool patterns
```

Example output:
```
Learned Patterns

navigate -> click -> type -> click
  Count: 5
  Examples: login_test, signup_test, checkout_test

navigate -> wait -> assert_text
  Count: 3
  Examples: homepage_test, about_test
```

### Knowledge Base

Stores learned information across test runs.

```bash
# View knowledge base
testtool knowledge
```

Example output:
```
Knowledge Base

Element mappings: 15
Routes: 8
Components: 12
API endpoints: 6

Sample Element Mappings:
  LoginButton: [data-testid="login-btn"]
  UsernameInput: input[name="username"]
```

### Source Analysis

Extract testing information from source code.

```bash
testtool analyze ./app/src --output analysis.json
```

Extracts:
- `data-testid` attributes
- React/Vue/Angular components
- Routes (Flask, Express, etc.)
- API endpoints
- Form structures

### Interactive Exploration

Explore websites interactively:

```bash
testtool explore https://example.com --headed
```

Available commands in exploration mode:
```
> click button#submit
> type input[name='search'] test query
> screenshot
> done
```

### Programmatic Usage

Create and execute tests via Python API:

```python
from testTool.models.action import Action, ActionType
from testTool.models.test_script import TestScript, TestStep
from testTool.executor import TestExecutor
from testTool.recorder import ScriptStorage

# Create test
script = TestScript(
    name="api_test",
    description="Programmatic test",
    steps=[
        TestStep(
            description="Load page",
            action=Action(
                type=ActionType.NAVIGATE,
                value="https://example.com"
            )
        ),
        TestStep(
            description="Click button",
            action=Action(
                type=ActionType.CLICK,
                selector="button#action"
            )
        )
    ]
)

# Save
storage = ScriptStorage()
storage.save(script, format='json')

# Execute
executor = TestExecutor(headless=True)
result = executor.execute_sync(script)

# Check results
if result.success:
    print("Test passed!")
else:
    for step in result.step_results:
        if not step.success:
            print(f"Step {step.step_index} failed: {step.error}")
```

### Using with LLM

Enable LLM-powered interpretation:

```bash
# Set API key
export OPENAI_API_KEY="your-key"

# Use LLM interpretation
testtool interpret "log in as admin with password secret123" --use-llm
```

The LLM can understand complex, multi-step instructions:
```
"Navigate to the login page, enter username 'admin' and password 'secret123', 
click the login button, and verify the dashboard is displayed"
```

## Best Practices

### 1. Use Stable Selectors

**Bad:**
```json
{
  "selector": "div > div > button:nth-child(3)"
}
```

**Good:**
```json
{
  "selector": "[data-testid='login-button']"
}
```

### 2. Add Expected Outcomes

Always document what each step should achieve:

```json
{
  "description": "Click login button",
  "expected_outcome": "User is redirected to dashboard",
  "action": {...}
}
```

### 3. Use Meaningful Names

**Bad:** `test1`, `test2`, `test3`

**Good:** `user_login_flow`, `checkout_process`, `search_functionality`

### 4. Group Related Tests

Use metadata tags:

```json
{
  "metadata": {
    "tags": ["authentication", "critical", "smoke-test"],
    "suite": "user-management"
  }
}
```

### 5. Take Screenshots Strategically

Don't screenshot every step. Focus on:
- Before/after important actions
- Verification points
- Error states

```json
{
  "description": "Verify dashboard loaded",
  "screenshot": true,
  "action": {...}
}
```

### 6. Handle Dynamic Content

For elements that load asynchronously:

```json
{
  "action": {
    "type": "wait",
    "value": "networkidle",
    "timeout": 30000
  }
}
```

### 7. Version Control Your Tests

Store test scripts in git:
```bash
git add test_scripts/
git commit -m "Add user registration tests"
```

### 8. Regular Maintenance

- Review and update selectors
- Remove obsolete tests
- Update expected outcomes
- Check learned patterns

### 9. Use Smart Mode for Internal Apps

If testing your own app:
1. Add `data-testid` attributes
2. Analyze source regularly
3. Use generated knowledge

### 10. Combine Modes

Use Smart Mode for setup/analysis:
```bash
testtool analyze ./app/src
```

Then use Dumb Mode for actual tests (more portable).

## Common Patterns

### Login Flow

```json
{
  "steps": [
    {"action": {"type": "navigate", "value": "https://app.com/login"}},
    {"action": {"type": "type", "selector": "input[name='username']", "value": "user"}},
    {"action": {"type": "type", "selector": "input[name='password']", "value": "pass"}},
    {"action": {"type": "click", "selector": "button[type='submit']"}},
    {"action": {"type": "wait", "value": "networkidle"}},
    {"action": {"type": "assert_element", "selector": ".dashboard"}}
  ]
}
```

### Form Submission

```json
{
  "steps": [
    {"action": {"type": "navigate", "value": "https://app.com/form"}},
    {"action": {"type": "type", "selector": "#name", "value": "John Doe"}},
    {"action": {"type": "type", "selector": "#email", "value": "john@example.com"}},
    {"action": {"type": "select", "selector": "#country", "value": "US"}},
    {"action": {"type": "click", "selector": "button#submit"}},
    {"action": {"type": "assert_text", "selector": ".success", "text": "Thank you"}}
  ]
}
```

### Multi-Page Navigation

```json
{
  "steps": [
    {"action": {"type": "navigate", "value": "https://app.com"}},
    {"action": {"type": "click", "selector": "a[href='/products']"}},
    {"action": {"type": "wait", "value": "load"}},
    {"action": {"type": "click", "selector": ".product:first-child"}},
    {"action": {"type": "wait", "value": "load"}},
    {"action": {"type": "screenshot", "value": "product_page"}}
  ]
}
```

## Troubleshooting

### Test Fails Intermittently

**Solution:** Increase timeouts or add explicit waits
```json
{
  "action": {
    "type": "wait",
    "value": "networkidle",
    "timeout": 60000
  }
}
```

### Element Not Found

**Solutions:**
1. Check selector in browser DevTools
2. Wait for element to appear
3. Use more specific selector
4. Check element is visible

### Screenshot Not Captured

**Solution:** Ensure screenshot directory exists and is writable
```bash
mkdir -p screenshots
chmod 755 screenshots
```

### Knowledge Base Not Updating

**Solution:** Ensure write permissions on knowledge_base directory
```bash
chmod 755 knowledge_base
```

## Next Steps

1. Create your test suite
2. Set up CI/CD integration
3. Monitor test execution
4. Refine selectors and patterns
5. Build knowledge base
6. Share tests with team
