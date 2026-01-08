"""
CLI module - Giao diện dòng lệnh cho Git Tag Manager.

Sử dụng rich và questionary để tạo giao diện terminal đẹp mắt.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary

from .core import (
    CONFIG_PATH,
    load_config,
    run_git,
    get_tag_info,
    get_current_branch,
    create_and_push_tag,
)

console = Console()


def main():
    """Entry point cho CLI."""
    console.print(Panel.fit("[bold blue]Git Tag Manager CLI[/bold blue]"))

    config = load_config()

    # Kiểm tra có projects không
    if not config.get('projects'):
        console.print(f"[red]No projects found in config file: {CONFIG_PATH}[/red]")
        console.print("Please run the GUI version to add projects, or create config manually.")
        sys.exit(1)

    # 1. Select Project
    proj_name = questionary.select(
        "Select Project:",
        choices=list(config['projects'].keys())
    ).ask()

    if not proj_name:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    project = config['projects'][proj_name]
    path = project['path']

    # 2. Select Strategy
    strategies = list(project.get('strategies', {}).keys())
    if not strategies:
        console.print(f"[red]No strategies defined for project '{proj_name}'[/red]")
        sys.exit(1)

    strat_name = questionary.select(
        "Select Strategy:",
        choices=strategies
    ).ask()

    if not strat_name:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    strategy = project['strategies'][strat_name]

    # 3. Calculate
    with console.status("[bold green]Calculating...[/bold green]"):
        curr_tag, next_tag = get_tag_info(path, strategy)
        branch = get_current_branch(path) or "Unknown"
        commit = run_git(['log', '-1', '--pretty=%s'], cwd=path, raise_on_error=False) or "Unknown"

    # 4. Show Table
    table = Table()
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Project Path", path)
    table.add_row("Branch", branch)
    table.add_row("Current Tag", curr_tag)
    table.add_row("NEXT TAG", f"[bold green]{next_tag}[/bold green]")

    # Truncate commit message nếu quá dài
    commit_display = commit[:50] + "..." if len(commit) > 50 else commit
    table.add_row("Commit", commit_display)
    console.print(table)

    # 5. Confirm & Execute
    if questionary.confirm(f"Create tag {next_tag} and PUSH?").ask():
        try:
            create_and_push_tag(path, next_tag)
            console.print(f"[green]✔ Tag {next_tag} created and pushed to origin.[/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    else:
        console.print("[yellow]Cancelled.[/yellow]")


if __name__ == "__main__":
    main()
