import typer
from rich.console import Console
from rich import print as rprint
from pathlib import Path
from typing import Optional

from .generator import ReadmeGenerator
from .providers import get_provider

app = typer.Typer(help="StarForge: AI-powered GitHub repo booster")
console = Console()


@app.command()
def generate_readme(
    path: str = typer.Argument(
        ".",
        help="Path to the project directory",
    ),
    provider: str = typer.Option(
        "ollama",
        "--provider",
        "-p",
        help="LLM provider to use: ollama, gemini, or openai",
    ),
    tone: str = typer.Option(
        "professional",
        "--tone",
        "-t",
        help="Tone for README: viral, professional, or minimal",
    ),
    output: str = typer.Option(
        "preview",
        "--output",
        "-o",
        help="Output mode: preview (print to console) or save (write to README.md)",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Specific model to use (e.g., mistral for ollama, gpt-4 for openai)",
    ),
    skip_llm: bool = typer.Option(
        False,
        "--skip-llm",
        help="Generate README without LLM (template only)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode for detailed error output",
    ),
) -> None:
    """Generate a professional README from your project.

    This command analyzes your project structure and generates a comprehensive README.md
    with proper formatting, badges, and sections. It can use various LLM providers for
    AI-powered content generation.

    Examples:

        # Generate with Ollama (default, local)
        starforge generate-readme .

        # Generate with Gemini API
        starforge generate-readme . --provider gemini

        # Generate with OpenAI
        starforge generate-readme . --provider openai --model gpt-4

        # Preview viral-toned README
        starforge generate-readme . --tone viral --output preview

        # Save professional README without LLM
        starforge generate-readme . --skip-llm --output save
    """
    try:
        # Validate path
        project_path = Path(path)
        if not project_path.exists():
            rprint(f"[red]✗ Project path does not exist: {path}[/red]")
            raise typer.Exit(1)

        # Validate tone
        valid_tones = ["viral", "professional", "minimal"]
        if tone not in valid_tones:
            rprint(f"[red]✗ Invalid tone: {tone}[/red]")
            rprint(f"[yellow]Valid tones: {', '.join(valid_tones)}[/yellow]")
            raise typer.Exit(1)

        # Validate output mode
        valid_outputs = ["preview", "save"]
        if output not in valid_outputs:
            rprint(f"[red]✗ Invalid output mode: {output}[/red]")
            rprint(f"[yellow]Valid modes: {', '.join(valid_outputs)}[/yellow]")
            raise typer.Exit(1)

        rprint(f"[bold cyan]🔨 Scanning project at {path}...[/bold cyan]")

        # Get LLM provider if not skipping
        llm_provider = None
        if not skip_llm:
            try:
                rprint(f"[cyan]Initializing {provider} provider...[/cyan]")
                # Build provider configuration
                provider_kwargs = {"model": model} if model else {}

                llm_provider = get_provider(provider, **provider_kwargs)

                if not llm_provider.is_available():
                    rprint(
                        f"[yellow]⚠️  {provider.upper()} provider not available. "
                        f"Using template-based generation.[/yellow]"
                    )
                    llm_provider = None
                else:
                    rprint(f"[green]✓ {provider.upper()} provider ready[/green]")
            except (ValueError, RuntimeError, ImportError) as e:
                rprint(f"[yellow]⚠️  Could not initialize {provider}: {e}[/yellow]")
                rprint(f"[yellow]Falling back to template-based generation...[/yellow]")
                llm_provider = None

        # Generate README
        rprint(f"[cyan]Generating {tone} README...[/cyan]")
        generator = ReadmeGenerator(
            project_path=str(project_path),
            provider=llm_provider,
            tone=tone,
        )

        readme_content = generator.generate()

        # Handle output
        if output == "preview":
            rprint("[bold green]✓ README Preview[/bold green]")
            rprint("-" * 80)
            console.print(readme_content)
            rprint("-" * 80)
            rprint(
                "\n[bold yellow]💡 Tip:[/bold yellow] "
                "Use --output save to save this to README.md"
            )
        elif output == "save":
            output_path = project_path / "README.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

            rprint(f"[bold green]✓ README saved to {output_path}[/bold green]")
            rprint(f"\n[cyan]Preview:[/cyan]")
            # Show first 50 lines as preview
            lines = readme_content.split("\n")[:50]
            console.print("\n".join(lines))
            if len(readme_content.split("\n")) > 50:
                rprint("\n[yellow]... (truncated, see README.md for full content)[/yellow]")

    except typer.Exit:
        raise
    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        if debug:
            raise
        raise typer.Exit(1)


@app.command()
def analyze():
    """Analyze your repo for star potential."""
    rprint("[bold blue]Analyzing repo health & star opportunities...[/bold blue]")


if __name__ == "__main__":
    app()
