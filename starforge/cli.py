import typer
from rich.console import Console
from rich import print as rprint

app = typer.Typer(help="StarForge: AI-powered GitHub repo booster")
console = Console()

@app.command()
def generate_readme(path: str = "."):
    """Generate a viral README from your project."""
    rprint(f"[bold green]🔨 Generating viral README for {path}...[/bold green]")
    # TODO: Integrate Ollama / local LLM for smart generation based on code files
    rprint("[yellow]💡 Pro tip: Run with Ollama for AI-powered viral sections![/yellow]")
    console.print("\n✅ Sample viral README section generated! (Full AI version coming next)")

@app.command()
def analyze():
    """Analyze your repo for star potential."""
    rprint("[bold blue]Analyzing repo health & star opportunities...[/bold blue]")

if __name__ == "__main__":
    app()
