"""
Murder Mystery Game - Main Entry Point

This is the main script to run the Murder Mystery investigation game.
The game uses LangGraph and LLM agents to create an interactive
detective experience where you play as Sherlock Holmes.

Usage:
    python app.py

Requirements:
    - OpenAI API key set in environment variable OPENAI_API_KEY
    - All dependencies from requirements.txt installed
"""

import os
import sys
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from agent.graph_builder import build_murder_mystery_game, visualize_graphs


def setup_api_key():
    """
    Ensures OpenAI API key is properly configured.
    
    Returns:
        bool: True if API key is set, False otherwise
    """
    if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
        console = Console()
        console.print("[yellow]OpenAI API key not found in environment.[/yellow]")
        api_key = getpass.getpass("Please enter your OpenAI API key: ")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            return True
        else:
            console.print("[red]API key is required to run the game.[/red]")
            return False
    return True


def get_game_parameters():
    """
    Prompts the user for game configuration parameters.
    
    Returns:
        tuple: (environment, max_characters, num_guesses_left, max_actions)
    """
    console = Console()
    
    console.print(Panel(
        "[bold cyan]Welcome to Murder Mystery Investigation![/bold cyan]\n\n"
        "You are Sherlock Holmes, the world's greatest detective.\n"
        "A murder has occurred and you must solve the case by:\n"
        "  • Interviewing suspects\n"
        "  • Gathering clues\n"
        "  • Identifying the killer\n\n"
        "[dim]Let's configure your investigation...[/dim]",
        border_style="cyan",
        title="🕵️‍♂️ Murder Mystery Game 🔍",
        title_align="left"
    ))
    
    # Get environment
    console.print("\n[bold]Step 1: Set the Scene[/bold]")
    console.print("[dim]Describe the setting where the murder took place.[/dim]")
    console.print("[dim]Examples: 'Victorian London mansion', 'Modern tech startup', 'Luxury cruise ship'[/dim]")
    environment = Prompt.ask(
        "[cyan]Environment[/cyan]",
        default="Mistral office in Paris"
    )
    
    # Get number of characters
    console.print("\n[bold]Step 2: Number of Characters[/bold]")
    console.print("[dim]How many characters should be in the story? (3-10 recommended)[/dim]")
    while True:
        try:
            max_characters = int(Prompt.ask(
                "[cyan]Number of characters[/cyan]",
                default="5"
            ))
            if max_characters < 3:
                console.print("[red]Please enter at least 3 characters (victim, killer, and suspect).[/red]")
            elif max_characters > 15:
                console.print("[yellow]Warning: More than 15 characters may make the game too complex.[/yellow]")
                if Prompt.ask("Continue anyway? (y/n)", default="n").lower() == 'y':
                    break
            else:
                break
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get number of guesses
    console.print("\n[bold]Step 3: Guess Limit[/bold]")
    console.print("[dim]How many guesses do you want to solve the case?[/dim]")
    while True:
        try:
            num_guesses_left = int(Prompt.ask(
                "[cyan]Number of guesses[/cyan]",
                default="3"
            ))
            if num_guesses_left < 1:
                console.print("[red]You need at least 1 guess![/red]")
            else:
                break
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get action limit (optional)
    console.print("\n[bold]Step 4: Action Limit (Optional)[/bold]")
    console.print("[dim]Set a maximum number of questions you can ask (leave empty for unlimited)[/dim]")
    console.print("[dim]Recommended: 15-20 for moderate difficulty[/dim]")
    max_actions = None
    action_input = Prompt.ask(
        "[cyan]Maximum actions (press Enter to skip)[/cyan]",
        default=""
    )
    if action_input.strip():
        try:
            max_actions = int(action_input)
            if max_actions < 1:
                console.print("[yellow]Invalid limit, using unlimited mode[/yellow]")
                max_actions = None
        except ValueError:
            console.print("[yellow]Invalid number, using unlimited mode[/yellow]")
            max_actions = None
    
    # Confirmation
    action_display = f"{max_actions}" if max_actions else "Unlimited"
    console.print(Panel(
        f"[bold]Game Configuration:[/bold]\n"
        f"  • Environment: [cyan]{environment}[/cyan]\n"
        f"  • Characters: [cyan]{max_characters}[/cyan]\n"
        f"  • Guesses: [cyan]{num_guesses_left}[/cyan]\n"
        f"  • Action Limit: [cyan]{action_display}[/cyan]",
        border_style="green",
        title="✅ Ready to Start",
        title_align="left"
    ))
    
    return environment, max_characters, num_guesses_left, max_actions


def main():
    """
    Main function to run the Murder Mystery game.
    """
    console = Console()
    
    # Setup API key
    if not setup_api_key():
        sys.exit(1)
    
    try:
        # Get game parameters
        environment, max_characters, num_guesses_left, max_actions = get_game_parameters()
        
        # Build the game graph
        console.print("\n[cyan]Generating your murder mystery...[/cyan]")
        console.print("[dim]This may take a moment...[/dim]\n")
        
        game_graph, conversation_graph = build_murder_mystery_game()
        
        # Optional: Visualize graphs (will show warning if graphviz not installed)
        # visualize_graphs(game_graph, conversation_graph, save_path="./graphs")
        
        # Prepare game state
        game_state = {
            "environment": environment,
            "max_characters": max_characters,
            "num_guesses_left": num_guesses_left,
        }
        
        # Add action limit if specified
        if max_actions:
            game_state["max_actions"] = max_actions
        
        # Run the game
        output = game_graph.invoke(game_state)
        
        # Game completed
        console.print("\n")
        console.print(Panel(
            "[bold]Thank you for playing Murder Mystery Investigation![/bold]\n\n"
            "[dim]The case has been closed.[/dim]",
            border_style="cyan",
            title="🎮 Game Over",
            title_align="left"
        ))
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Game interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

