# Example Test Scripts

This directory contains example test scripts demonstrating the browser testing tool's capabilities.

## Examples

### 1. basic_navigation.json
Simple navigation and assertion test.

### 2. search_workflow.json
Search interaction demonstration.

## Running Examples

```bash
# Execute an example
testtool execute examples/basic_navigation

# Execute in headed mode (see the browser)
testtool execute examples/search_workflow --headed

# List all examples
testtool list-scripts
```

## Creating Your Own Tests

### Interactive Recording
```bash
testtool record --name my_test --description "My custom test" --mode dumb
```

### Programmatic Creation
See the Python examples in the main README.md
