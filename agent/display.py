"""
Display and UI functions for the Murder Mystery game.

This module provides all the user interface functions using rich console
for styling, formatting, and interactive prompts.
"""

from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.box import HEAVY_EDGE
from rich.table import Table
from rich.text import Text


def print_game_header():
    """
    Displays the main header for the Murder Mystery Investigation game.
    """
    console = Console()
    console.print("""
    [bold blue on white]═══════════════════════════════════════════════════════════[/bold blue on white]
    [bold blue on white]   🕵️‍♂️  MURDER MYSTERY INVESTIGATION 🔍                  [/bold blue on white]
    [bold blue on white]═══════════════════════════════════════════════════════════[/bold blue on white]
    """, justify="center")


def print_narration(narration):
    """
    Prints the narration dialogue from Dr. John Watson with styled formatting.

    Args:
        narration: The LLM response object containing the narration content in its 'content' attribute.
    """
    console = Console()
    console.print(Panel(
        f"[bold] Dr. John Watson [/bold]:\n\n{narration.content}",
        border_style="blue",
        padding=(1, 2),
        title="💬 Dialogue",
        title_align="left"
    ))
    console.rule(style="blue")


def print_introduction(character, narration):
    """
    Displays the introduction dialogue for a character with styled formatting.

    Args:
        character: Character object containing character information.
        narration: LLM response object containing the narration content in its 'content' attribute.
    """
    console = Console()
    console.rule(f"[bold blue]Conversation with {character.name}[/bold blue]", style="blue")
    console.print(Panel(
        f"[bold]{character.name}[/bold]:\n\n{narration.content}",
        border_style="blue",
        padding=(1, 2),
        title="💬 Dialogue",
        title_align="left"
    ))
    console.rule(style="blue")


def get_player_input(character_name):
    """
    Prompts the player for input during character interactions.

    Args:
        character_name (str): Name of the character being questioned.

    Returns:
        str: The player's input question or 'EXIT' to end the conversation.
    """
    console = Console()

    # Show input instructions
    console.print(Panel(
        f"[bold blue]Ask your question to {character_name}[/bold blue]\n"
        f"[dim]Type 'EXIT' to end conversation[/dim]",
        box=HEAVY_EDGE,
        border_style="blue",
        padding=(1, 2),
        title="💭 Your Question",
        title_align="left"
    ))

    # Custom prompt with styling
    question = Prompt.ask(
        "[bold yellow]Detective[/bold yellow]",
        default="",
        show_default=False
    )

    # Echo the input in a panel for better visibility
    if question.lower() != 'exit':
        console.print(Panel(
            f"[italic]{question}[/italic]",
            border_style="yellow",
            padding=(1, 1),
            title="🔍 Asked",
            title_align="left"
        ))

    return question


def print_character_answer(character, reaction):
    """
    Displays a character's answer with styled formatting.

    Args:
        character: Character object containing character information.
        reaction (str): The character's response or reaction as generated from the LLM.
    """
    console = Console()
    console.print(Panel(
        f"[bold]{character.name}'s Answer[/bold]:\n\n[italic]{reaction}[/italic]",
        border_style="cyan",
        padding=(1, 2),
        title="🗣️ Answer",
        title_align="left"
    ))


def print_characters_list(characters):
    """
    Displays a formatted table of all characters in the game with their backgrounds.

    Args:
        characters (list): List of character objects containing name, role, and backstory.

    Returns:
        dict: Mapping of displayed positions to original character indices.
    """
    import random
    
    console = Console()

    # Create title
    console.print("\n[bold blue]CHARACTERS[/bold blue]", justify="center")

    # Create list of indices and characters
    char_list = list(enumerate(characters))
    random.shuffle(char_list)

    # Create and populate table
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=HEAVY_EDGE,
        expand=True
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold cyan", width=20)
    table.add_column("Background", style="green")

    # Create mapping of displayed position to original index
    display_to_original = {}

    for display_pos, (orig_idx, character) in enumerate(char_list):
        # Add victim note to name if applicable
        name_text = f"{character.name} {'[red](victim)[/red]' if character.role == 'Victim' else ''}"

        table.add_row(
            str(display_pos + 1),
            name_text,
            Text(character.backstory, overflow="fold")
        )
        display_to_original[display_pos] = orig_idx
        # Add border between rows
        if display_pos < len(char_list) - 1:
            table.add_row(style="dim")

    console.print(table)
    return display_to_original


def get_character_selection(characters, display_to_original):
    """
    Handles the player's character selection for investigation during the game.

    Args:
        characters (list): List of character objects.
        display_to_original (dict): Mapping of displayed positions to original indices.

    Returns:
        dict: Contains selected_character_id (None if player chooses to guess the killer).

    Note:
        Returns -1 when player wants to guess the killer.
        Validates input and prevents selection of the victim.
    """
    console = Console()

    while True:
        try:
            # Create selection prompt
            console.print(Panel(
                "[bold blue]Enter the number of the character to investigate[/bold blue]\n"
                "[dim]Enter -1 to Guess the Killer[/dim]",
                border_style="blue",
                title="👤 Selection",
                title_align="left"
            ))

            # Get user input
            choice = Prompt.ask(
                "[bold yellow]Detective[/bold yellow]",
                default="-1",
                show_default=False
            )

            # Convert to int and validate
            choice = int(choice)

            if choice == -1:
                return {"selected_character_id": None}

            if 0 < choice <= len(characters):
                # Map displayed choice to original index
                original_idx = display_to_original[choice - 1]
                selected_character = characters[original_idx]

                if selected_character.role == 'Victim':
                    console.print("[red]Invalid input. You are unable to choose the victim[/red]")
                    continue

                # Show selection confirmation
                console.print(f"[green]You have selected {selected_character.name}[/green]")
                return {"selected_character_id": original_idx}

            console.print("[red]Invalid input. Please enter a number within the range or -1.[/red]")

        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")
        except KeyError:
            console.print("[red]Invalid selection. Please try again.[/red]")


def get_player_yesno_answer(question):
    """
    Prompts the player for a yes/no response regarding Sherlock AI assistance.

    Args:
        question (str): The player instruction/question to display to the player.

    Returns:
        str: Player's response ('y' for yes, 'n' for no/exit)
    """
    console = Console()

    # Show input instructions
    console.print(Panel(
        f"[bold blue]{question}[/bold blue]\n"
        f"enter 'y' to get his help or 'n' to ask by yourself or exit",
        box=HEAVY_EDGE,
        border_style="blue",
        padding=(1, 2),
        title="🤖🕵️ Sherlock AI",
        title_align="left"
    ))

    # Custom prompt with styling
    answer = Prompt.ask(
        "[bold yellow]Detective[/bold yellow]",
        default="",
        show_default=False
    )
    return answer


def print_suspect_list(characters):
    """
    Displays a formatted table of all suspects in the investigation.

    Args:
        characters (list): List of character objects to be displayed as suspects.
    """
    console = Console()

    # Create and populate table
    table = Table(
        show_header=True,
        header_style="bold bright_red",
        box=HEAVY_EDGE,
        expand=True,
        title="[bold bright_red]🔍 Suspects[/bold bright_red]"
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold bright_red")

    # Sort characters by name
    characters = sorted(characters, key=lambda x: x.name)
    for idx, character in enumerate(characters, 1):
        table.add_row(str(idx), character.name)

    console.print(table)


def print_guesses_remaining(num_guesses):
    """
    Displays the number of remaining guesses available to the player.

    Args:
        num_guesses (int): Number of guesses remaining.
    """
    console = Console()
    console.print(Panel(
        f"[bold]You have {num_guesses} {'guess' if num_guesses == 1 else 'guesses'} remaining[/bold]",
        border_style="yellow",
        title="⏳ Guesses",
        title_align="left"
    ))


def print_result(is_win, is_lose, killer_name=None):
    """
    Displays the game result message indicating whether the player won or lost.

    Args:
        is_win (bool): True if player won the game.
        is_lose (bool): True if player lost the game.
        killer_name (str, optional): Name of the killer to reveal if player lost.
    """
    console = Console()
    if is_win:
        console.print(Panel(
            "[bold green]Congratulations! You have correctly identified the killer.[/bold green]",
            border_style="green",
            title="🎯 Success",
            title_align="left"
        ))
    elif is_lose:
        console.print(Panel(
            f"[bold bright_red]Investigation Failed![/bold bright_red]\n[bright_red]The killer was {killer_name}.[/bright_red]",
            border_style="bright_red",
            title="❌ Game Over",
            title_align="left"
        ))


def print_incorrect_guess():
    """
    Displays a message indicating that the player's guess was incorrect.
    """
    console = Console()
    console.print(Panel(
        "[bold yellow]The person you chose was innocent.[/bold yellow]",
        border_style="yellow",
        title="❗ Wrong Guess",
        title_align="left"
    ))


def print_sherlock_question(question_content):
    """
    Displays a question asked by Sherlock AI.
    
    Args:
        question_content (str): The question content to display.
    """
    console = Console()
    console.print(Panel(
        f"[italic]{question_content}[/italic]",
        border_style="yellow",
        padding=(1, 1),
        title="🔍 Asked by Sherlock AI 🤖🕵️",
        title_align="left"
    ))

