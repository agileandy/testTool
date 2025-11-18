"""Main CLI interface for the browser testing tool."""

import click
import asyncio
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models.action import Action, ActionType
from .models.test_script import TestScript, TestStep
from .browser_control import PlaywrightController
from .nl_processor import NLInterpreter
from .recorder import TestRecorder, ScriptStorage
from .executor import TestExecutor
from .learning_layer import PatternLearner, KnowledgeBase
from .utils import SourceAnalyzer

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Browser-Based Automated Testing Builder
    
    A deterministic browser-driven testing tool that executes natural-language
    test instructions and builds reusable regression suites.
    """
    pass


@cli.command()
@click.option('--name', required=True, help='Test script name')
@click.option('--description', required=True, help='Test description')
@click.option('--mode', type=click.Choice(['dumb', 'smart']), default='dumb', help='Operating mode')
@click.option('--interactive/--no-interactive', default=True, help='Interactive mode')
def record(name, description, mode, interactive):
    """Record a new test script."""
    recorder = TestRecorder()
    recorder.start_recording(name, description, mode)
    
    console.print(f"[green]Recording started:[/green] {name}")
    console.print(f"Mode: {mode}")
    
    if interactive:
        console.print("\n[yellow]Enter commands (type 'done' to finish):[/yellow]")
        
        interpreter = NLInterpreter(use_llm=False)
        step_num = 1
        
        while True:
            command = click.prompt(f"Step {step_num}", type=str)
            
            if command.lower() in ['done', 'quit', 'exit']:
                break
            
            # Interpret the command
            actions = interpreter.interpret(command)
            
            if not actions:
                console.print("[red]Could not interpret command. Try again.[/red]")
                continue
            
            # Record each action
            for action in actions:
                recorder.record_step(
                    description=command,
                    action=action,
                    screenshot=False
                )
            
            console.print(f"[green]✓[/green] Recorded: {command}")
            step_num += 1
    
    # Stop recording and save
    script = recorder.stop_recording()
    storage = ScriptStorage()
    filepath = storage.save(script, format='json')
    
    console.print(f"\n[green]✓ Test script saved:[/green] {filepath}")
    console.print(f"Total steps: {len(script.steps)}")


@cli.command()
@click.argument('script_name')
@click.option('--headless/--headed', default=True, help='Browser mode')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Script format')
def execute(script_name, headless, format):
    """Execute a test script."""
    console.print(f"[blue]Loading test script:[/blue] {script_name}")
    
    try:
        storage = ScriptStorage()
        script = storage.load(script_name, format=format)
        
        console.print(f"[green]Loaded:[/green] {script.name}")
        console.print(f"Steps: {len(script.steps)}")
        console.print(f"Mode: {script.mode}")
        
        # Execute
        console.print("\n[yellow]Executing...[/yellow]")
        executor = TestExecutor(headless=headless)
        result = executor.execute_sync(script)
        
        # Display results
        console.print("\n[bold]Execution Results[/bold]")
        console.print(f"Success: {'✓' if result.success else '✗'}")
        console.print(f"Duration: {result.total_duration_ms:.2f}ms")
        console.print(f"Steps passed: {sum(1 for s in result.step_results if s.success)}/{len(result.step_results)}")
        
        # Show failed steps
        failed = [s for s in result.step_results if not s.success]
        if failed:
            console.print("\n[red]Failed steps:[/red]")
            for step in failed:
                console.print(f"  Step {step.step_index}: {step.error}")
        
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Script '{script_name}' not found")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
def list_scripts():
    """List all available test scripts."""
    storage = ScriptStorage()
    scripts = storage.list_scripts()
    
    if not scripts:
        console.print("[yellow]No test scripts found.[/yellow]")
        return
    
    table = Table(title="Available Test Scripts")
    table.add_column("Name", style="cyan")
    
    for script in scripts:
        table.add_row(script)
    
    console.print(table)


@cli.command()
@click.argument('instruction')
@click.option('--use-llm/--no-llm', default=False, help='Use LLM for interpretation')
def interpret(instruction, use_llm):
    """Interpret a natural language instruction."""
    interpreter = NLInterpreter(use_llm=use_llm)
    actions = interpreter.interpret(instruction)
    
    console.print(f"[blue]Instruction:[/blue] {instruction}")
    console.print(f"\n[green]Interpreted as {len(actions)} action(s):[/green]")
    
    for i, action in enumerate(actions, 1):
        console.print(f"\n{i}. {action.type}")
        if action.selector:
            console.print(f"   Selector: {action.selector}")
        if action.value:
            console.print(f"   Value: {action.value}")
        if action.text:
            console.print(f"   Text: {action.text}")


@cli.command()
@click.argument('source_dir')
@click.option('--output', '-o', help='Output file for analysis results')
def analyze(source_dir, output):
    """Analyze application source code (Smart Mode)."""
    console.print(f"[blue]Analyzing source:[/blue] {source_dir}")
    
    try:
        analyzer = SourceAnalyzer(source_dir)
        results = analyzer.analyze()
        
        console.print("\n[green]Analysis Results:[/green]")
        console.print(f"Test IDs found: {len(results['test_ids'])}")
        console.print(f"Routes found: {len(results['routes'])}")
        console.print(f"Components found: {len(results['components'])}")
        console.print(f"API endpoints found: {len(results['api_endpoints'])}")
        
        if results['test_ids']:
            console.print("\n[cyan]Sample Test IDs:[/cyan]")
            for test_id in results['test_ids'][:5]:
                console.print(f"  - {test_id['id']} ({test_id['file']})")
        
        if results['routes']:
            console.print("\n[cyan]Routes:[/cyan]")
            for route in results['routes'][:10]:
                console.print(f"  - {route}")
        
        # Save to file if requested
        if output:
            output_path = Path(output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]✓ Results saved to:[/green] {output_path}")
        
        # Update knowledge base
        kb = KnowledgeBase()
        for test_id in results['test_ids']:
            kb.add_element_mapping(
                test_id['id'],
                test_id['selector'],
                selector_type='testid'
            )
        for route in results['routes']:
            kb.add_route(route)
        
        console.print("\n[green]✓ Knowledge base updated[/green]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
def patterns():
    """Show learned patterns."""
    learner = PatternLearner()
    common_patterns = learner.get_common_patterns(min_count=1)
    
    if not common_patterns:
        console.print("[yellow]No patterns learned yet.[/yellow]")
        return
    
    console.print("[bold]Learned Patterns[/bold]\n")
    
    for pattern in common_patterns[:10]:
        console.print(f"[cyan]{pattern['pattern']}[/cyan]")
        console.print(f"  Count: {pattern['count']}")
        console.print(f"  Examples: {', '.join(pattern['examples'][:3])}")
        console.print()


@cli.command()
def knowledge():
    """Show knowledge base contents."""
    kb = KnowledgeBase()
    catalog = kb.export_catalog()
    
    console.print("[bold]Knowledge Base[/bold]\n")
    
    console.print(f"Element mappings: {catalog['stats']['total_mappings']}")
    console.print(f"Routes: {catalog['stats']['total_routes']}")
    console.print(f"Components: {catalog['stats']['total_components']}")
    console.print(f"API endpoints: {catalog['stats']['total_endpoints']}")
    
    if catalog['element_mappings']:
        console.print("\n[cyan]Sample Element Mappings:[/cyan]")
        for name, mapping in list(catalog['element_mappings'].items())[:5]:
            selectors = mapping.get('selectors', [])
            if selectors:
                console.print(f"  {name}: {selectors[0]['value']}")


@cli.command()
@click.argument('url')
@click.option('--headless/--headed', default=False, help='Browser mode')
def explore(url, headless):
    """Interactively explore a website."""
    console.print(f"[blue]Opening:[/blue] {url}")
    console.print("[yellow]Interactive exploration mode[/yellow]")
    console.print("Commands: click <selector>, type <selector> <text>, screenshot, done")
    
    async def run_exploration():
        controller = PlaywrightController(headless=headless)
        await controller.start()
        
        try:
            # Navigate to URL
            await controller._navigate(url)
            console.print(f"[green]✓ Loaded:[/green] {url}")
            
            while True:
                command = click.prompt("\nCommand", type=str)
                
                if command.lower() in ['done', 'quit', 'exit']:
                    break
                
                parts = command.split(maxsplit=2)
                if not parts:
                    continue
                
                action_type = parts[0].lower()
                
                try:
                    if action_type == 'click' and len(parts) >= 2:
                        selector = parts[1]
                        action = Action(type=ActionType.CLICK, selector=selector)
                        result = await controller.execute_action(action)
                        if result['success']:
                            console.print("[green]✓ Clicked[/green]")
                        else:
                            console.print(f"[red]✗ {result.get('error')}[/red]")
                    
                    elif action_type == 'type' and len(parts) >= 3:
                        selector = parts[1]
                        value = parts[2]
                        action = Action(type=ActionType.TYPE, selector=selector, value=value)
                        result = await controller.execute_action(action)
                        if result['success']:
                            console.print("[green]✓ Typed[/green]")
                        else:
                            console.print(f"[red]✗ {result.get('error')}[/red]")
                    
                    elif action_type == 'screenshot':
                        action = Action(type=ActionType.SCREENSHOT)
                        result = await controller.execute_action(action)
                        if result['success']:
                            console.print(f"[green]✓ Screenshot saved:[/green] {result['metadata']['screenshot_path']}")
                        else:
                            console.print(f"[red]✗ {result.get('error')}[/red]")
                    
                    else:
                        console.print("[yellow]Unknown command[/yellow]")
                
                except Exception as e:
                    console.print(f"[red]Error:[/red] {str(e)}")
        
        finally:
            await controller.stop()
    
    asyncio.run(run_exploration())


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()

