import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from database import Database

app = typer.Typer(help="A lightweight CLI tool for managing small teams of 3-5 people")
console = Console()
db = Database()

task_app = typer.Typer(help="Task management commands")
doc_app = typer.Typer(help="Document indexing and search")
team_app = typer.Typer(help="Team analysis commands")

app.add_typer(task_app, name="task")
app.add_typer(doc_app, name="doc")
app.add_typer(team_app, name="team")


@task_app.command("assign")
def task_assign(title: str, assignee: str):
    """Assign a new task to a team member"""
    task_id = db.create_task(title, assignee)
    console.print(f"[green]Task #{task_id} assigned to {assignee}[/green]")


@task_app.command("status")
def task_status(task_id: int, status: str):
    """Update task status (todo/in-progress/done)"""
    db.update_task_status(task_id, status)
    console.print(f"[green]Task #{task_id} status updated to {status}[/green]")


@task_app.command("list")
def task_list():
    """List all tasks"""
    tasks = db.get_all_tasks()
    
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Assignee", style="yellow")
    table.add_column("Status", style="green")
    
    for task in tasks:
        table.add_row(str(task[0]), task[1], task[2], task[3])
    
    console.print(table)


@doc_app.command("index")
def doc_index(path: str):
    """Index documents from a directory"""
    doc_path = Path(path)
    if not doc_path.exists():
        console.print(f"[red]Path {path} does not exist[/red]")
        return
    
    count = 0
    if doc_path.is_file():
        db.index_document(str(doc_path))
        count = 1
    else:
        for file in doc_path.rglob("*.txt"):
            db.index_document(str(file))
            count += 1
        for file in doc_path.rglob("*.md"):
            db.index_document(str(file))
            count += 1
    
    console.print(f"[green]Indexed {count} documents[/green]")


@doc_app.command("search")
def doc_search(query: str):
    """Search indexed documents"""
    results = db.search_documents(query)
    
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return
    
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Path", style="cyan")
    table.add_column("Preview", style="white")
    
    for result in results:
        preview = result[1][:100] + "..." if len(result[1]) > 100 else result[1]
        table.add_row(result[0], preview)
    
    console.print(table)


@team_app.command("analyze")
def team_analyze():
    """Analyze team composition and skills"""
    members = db.get_team_members()
    
    if not members:
        console.print("[yellow]No team members found. Add members first.[/yellow]")
        return
    
    table = Table(title="Team Analysis")
    table.add_column("Member", style="cyan")
    table.add_column("Skills", style="green")
    
    for member in members:
        table.add_row(member[1], member[2])
    
    console.print(table)


@team_app.command("gaps")
def team_gaps():
    """Identify skill gaps in the team"""
    gaps = db.get_skill_gaps()
    
    table = Table(title="Skill Gaps")
    table.add_column("Skill", style="yellow")
    table.add_column("Priority", style="red")
    
    for gap in gaps:
        table.add_row(gap[1], gap[2])
    
    console.print(table)


@team_app.command("add-member")
def add_member(name: str, skills: str):
    """Add a team member with their skills"""
    db.add_team_member(name, skills)
    console.print(f"[green]Added {name} to the team[/green]")


@team_app.command("add-gap")
def add_gap(skill: str, priority: str = "medium"):
    """Add a skill gap (priority: low/medium/high)"""
    db.add_skill_gap(skill, priority)
    console.print(f"[green]Added skill gap: {skill} (priority: {priority})[/green]")


if __name__ == "__main__":
    app()
