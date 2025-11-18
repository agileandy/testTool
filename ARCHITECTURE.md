# Architecture Documentation

## Overview

The Browser-Based Automated Testing Builder is a modular, deterministic testing tool built on the following architectural principles:

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Determinism**: Same input always produces same output
3. **Extensibility**: Easy to add new features without breaking existing code
4. **Testability**: All components can be tested in isolation

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                      (main.py)                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┴──────────────────────────────┐
    │                                             │
┌───▼────────────────┐                 ┌─────────▼───────────┐
│  NL Processor      │                 │  Source Analyzer    │
│  (nl_processor/)   │                 │  (utils/)           │
└───┬────────────────┘                 └─────────┬───────────┘
    │                                             │
    │  Actions                                    │  Knowledge
    │                                             │
┌───▼────────────────┐                 ┌─────────▼───────────┐
│  Test Recorder     │◄────────────────┤  Knowledge Base     │
│  (recorder/)       │                 │  (learning_layer/)  │
└───┬────────────────┘                 └─────────────────────┘
    │                                             │
    │  TestScript                                 │  Patterns
    │                                             │
┌───▼────────────────┐                 ┌─────────▼───────────┐
│  Script Storage    │                 │  Pattern Learner    │
│  (recorder/)       │                 │  (learning_layer/)  │
└───┬────────────────┘                 └─────────────────────┘
    │
    │  TestScript
    │
┌───▼────────────────┐
│  Test Executor     │
│  (executor/)       │
└───┬────────────────┘
    │
    │  Actions
    │
┌───▼────────────────┐
│  Browser Control   │
│  (browser_control/)│
└────────────────────┘
```

## Core Components

### 1. Models (`models/`)

**Purpose**: Define data structures used throughout the system

**Components**:
- `action.py`: Action and ActionType definitions
- `test_script.py`: TestScript and TestStep definitions
- `execution_result.py`: ExecutionResult and StepResult definitions

**Design Decisions**:
- Uses Pydantic for validation and serialization
- Immutable by design (prevents accidental state changes)
- Supports JSON/YAML serialization out of the box

### 2. Browser Control (`browser_control/`)

**Purpose**: Provide deterministic browser automation

**Components**:
- `PlaywrightController`: Manages browser lifecycle and action execution

**Key Features**:
- Deterministic viewport (1280x720)
- Explicit waits for all actions
- Screenshot and DOM snapshot capabilities
- Support for multiple browsers (Chromium, Firefox, WebKit)

**Design Decisions**:
- Async/await for all operations (better concurrency)
- Prefer data-testid selectors for stability
- Always wait for DOM state before actions
- Capture execution metadata for debugging

### 3. Natural Language Processor (`nl_processor/`)

**Purpose**: Convert human instructions to structured actions

**Components**:
- `NLInterpreter`: Interprets natural language commands

**Operating Modes**:
1. **Rule-based**: Pattern matching for common commands
2. **LLM-based**: Uses OpenAI/Anthropic for complex interpretation

**Design Decisions**:
- Falls back to rule-based if LLM unavailable
- Low temperature (0.1) for deterministic LLM output
- Validates actions before returning
- Maintains context for multi-step interpretations

### 4. Recorder (`recorder/`)

**Purpose**: Record browser interactions as test scripts

**Components**:
- `TestRecorder`: Captures interactions in real-time
- `ScriptStorage`: Persists scripts to disk

**Supported Formats**:
- JSON (default, best for version control)
- YAML (human-readable)

**Design Decisions**:
- State machine pattern (not recording → recording → stopped)
- Captures metadata for reproducibility
- Sanitizes filenames for cross-platform compatibility
- Supports both formats for flexibility

### 5. Executor (`executor/`)

**Purpose**: Execute test scripts deterministically

**Components**:
- `TestExecutor`: Orchestrates test execution

**Key Features**:
- Executes scripts step-by-step
- Captures detailed results for each step
- Takes screenshots on demand or failure
- Saves execution results for analysis

**Design Decisions**:
- Each execution is independent (new browser instance)
- Always cleanup resources (even on failure)
- Provides both async and sync execution methods
- Detailed error reporting with context

### 6. Learning Layer (`learning_layer/`)

**Purpose**: Learn from executions to improve future tests

**Components**:
- `PatternLearner`: Identifies common workflows
- `KnowledgeBase`: Stores learned information

**Capabilities**:
- Pattern recognition across multiple scripts
- Selector suggestion based on history
- Workflow similarity detection
- Auto-generation of test scaffolds

**Design Decisions**:
- Incremental learning (updates on each observation)
- Persistent storage (survives restarts)
- Separate concerns (patterns vs. knowledge)
- Uses simple algorithms for speed (can be enhanced)

### 7. Utilities (`utils/`)

**Purpose**: Provide helper functionality

**Components**:
- `SourceAnalyzer`: Analyzes application source code

**Smart Mode Features**:
- Finds data-testid attributes
- Extracts routes (Flask, React Router, etc.)
- Discovers components
- Identifies API endpoints

**Design Decisions**:
- Regex-based parsing (fast, no AST needed)
- Supports multiple frameworks
- Extensible pattern system
- Fails gracefully on parse errors

## Data Flow

### Recording Flow

```
User Input (CLI)
    ↓
NL Interpreter → Actions
    ↓
Test Recorder → TestScript
    ↓
Script Storage → File System (JSON/YAML)
    ↓
Pattern Learner → Knowledge Base
```

### Execution Flow

```
Script Storage → TestScript
    ↓
Test Executor
    ↓
Browser Controller → Browser
    ↓
Execution Results → File System
    ↓
Pattern Learner (optional)
```

### Smart Mode Analysis Flow

```
Source Files
    ↓
Source Analyzer → Analysis Results
    ↓
Knowledge Base → Persistent Storage
    ↓
Available to NL Interpreter & Test Recorder
```

## Determinism Strategy

### 1. Browser Level
- Fixed viewport size
- Consistent user agent
- Explicit waits (no sleep/arbitrary delays)
- DOM state verification before actions

### 2. Script Level
- Ordered execution (no parallelism within script)
- Same script produces same action sequence
- Deterministic selectors (prefer stable IDs)

### 3. Data Level
- Remove timestamps from snapshots
- Hash DOM content for comparison
- Filter out non-deterministic attributes

### 4. Execution Level
- Isolated browser instances per run
- Clean state for each execution
- No shared global state

## Extensibility Points

### 1. New Action Types
Add to `ActionType` enum and implement in `PlaywrightController.execute_action()`

### 2. New Storage Formats
Implement in `ScriptStorage.save()` and `ScriptStorage.load()`

### 3. New NL Patterns
Add patterns to `NLInterpreter._interpret_with_rules()`

### 4. New Analysis Patterns
Add regex patterns to `SourceAnalyzer`

### 5. Custom Learning Algorithms
Extend `PatternLearner` with new pattern detection methods

## Error Handling

### Strategy
- Fail fast at validation time
- Graceful degradation at execution time
- Detailed error messages with context
- Never lose recorded data

### Levels
1. **Validation Errors**: Caught before execution
2. **Execution Errors**: Caught per-step, don't stop test
3. **Fatal Errors**: Browser crashes, cleanup and report

## Performance Considerations

### Bottlenecks
- Browser startup (3-5 seconds)
- Page loads (network dependent)
- LLM API calls (1-3 seconds)

### Optimizations
- Reuse browser context when possible
- Cache LLM interpretations
- Parallel test execution (future)
- Smart waiting (wait for specific conditions, not fixed time)

## Security Considerations

### Secrets Management
- Never store credentials in scripts
- Use environment variables for API keys
- Sanitize logs and screenshots

### Sandbox Isolation
- Each execution in isolated context
- No access to host file system (except designated dirs)
- Network isolation for sensitive tests

## Testing Strategy

### Unit Tests
- Each component tested in isolation
- Mock external dependencies (browser, LLM)
- Fast execution (no real browser)

### Integration Tests
- Component interactions
- Real browser (headless)
- Temporary file systems

### End-to-End Tests
- Full workflow tests
- Real applications
- Manual verification

## Future Enhancements

### Short Term
1. Parallel test execution
2. Visual regression testing
3. Network request/response capture
4. Better error recovery

### Medium Term
1. Test generation from user sessions
2. Advanced pattern recognition (ML-based)
3. Cross-browser compatibility checks
4. Performance metrics capture

### Long Term
1. Distributed execution
2. Cloud-based test management
3. AI-powered test maintenance
4. Self-healing tests

## Dependencies

### Core
- **Playwright**: Browser automation (1.40.0+)
- **Pydantic**: Data validation (2.5.0+)
- **Click**: CLI framework (8.1.0+)

### Optional
- **OpenAI**: LLM integration
- **Anthropic**: Alternative LLM
- **Rich**: Terminal UI

### Development
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)

### Directory Structure
```
./test_scripts/       # Saved test scripts
./screenshots/        # Test execution screenshots
./test_results/       # Execution result logs
./knowledge_base/     # Learned patterns and mappings
```

## Maintenance

### Adding New Features
1. Design with determinism in mind
2. Add tests first (TDD)
3. Update documentation
4. Ensure backward compatibility

### Debugging
1. Check execution result logs
2. Review screenshots
3. Enable verbose logging
4. Use browser headed mode

### Performance Tuning
1. Profile with real workloads
2. Optimize hot paths
3. Cache aggressively
4. Monitor resource usage
