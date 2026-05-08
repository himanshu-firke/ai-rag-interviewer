"""
RAG Logger — Rich terminal logging for the RAG pipeline.
Displays detailed information about each step: retrieval, sources,
confidence scores, context previews, and evaluation results.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True, width=120)


def get_logger():
    return console


def log_session_start(candidate_name: str, role: str, skills: list, technologies: list, experience: str):
    """Log when a new interview session starts."""
    table = Table(title="NEW INTERVIEW SESSION", box=box.DOUBLE_EDGE, border_style="cyan", width=100)
    table.add_column("Field", style="bold white", width=20)
    table.add_column("Value", style="green")
    table.add_row("Candidate", candidate_name)
    table.add_row("Role", role)
    table.add_row("Experience", experience)
    table.add_row("Skills", ", ".join(skills[:10]) if skills else "N/A")
    table.add_row("Technologies", ", ".join(technologies[:8]) if technologies else "N/A")
    console.print()
    console.print(table)
    console.print()


def log_resume_parsed(name: str, skills: list, technologies: list, experience: str, summary: str):
    """Log resume parsing results."""
    panel = Panel(
        f"[bold white]Name:[/] {name}\n"
        f"[bold white]Experience Level:[/] [yellow]{experience}[/]\n"
        f"[bold white]Skills:[/] {', '.join(skills[:12])}\n"
        f"[bold white]Technologies:[/] {', '.join(technologies[:10])}\n"
        f"[bold white]Summary:[/] {summary[:200]}",
        title="[bold cyan]RESUME PARSED[/]",
        border_style="cyan",
        width=100,
    )
    console.print(panel)


def log_retrieval_queries(queries: list):
    """Log the retrieval queries being sent to the vector store."""
    console.print("\n[bold magenta]RAG RETRIEVAL QUERIES[/]")
    for i, q in enumerate(queries):
        console.print(f"  [dim]{i+1}.[/] [white]{q}[/]")
    console.print()


def log_retrieved_chunks(documents: list, metadatas: list, distances: list):
    """Log retrieved chunks with source, page, confidence, and preview."""
    table = Table(
        title="RETRIEVED CONTEXT CHUNKS",
        box=box.ROUNDED,
        border_style="green",
        width=110,
        show_lines=True,
    )
    table.add_column("#", style="bold", width=3, justify="center")
    table.add_column("Source", style="cyan", width=30)
    table.add_column("Page", style="yellow", width=5, justify="center")
    table.add_column("Confidence", style="bold", width=12, justify="center")
    table.add_column("Preview", style="white", width=55)

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        source = meta.get("source", "Unknown")[:28]
        page = str(meta.get("page", "?"))
        # Convert distance to confidence (cosine: lower distance = higher confidence)
        confidence = max(0, round((1 - dist) * 100, 1))
        conf_color = "green" if confidence >= 70 else "yellow" if confidence >= 50 else "red"
        conf_str = f"[{conf_color}]{confidence}%[/{conf_color}]"
        preview = doc[:80].replace("\n", " ").strip() + "..."

        table.add_row(str(i + 1), source, page, conf_str, preview)

    console.print(table)


def log_question_generated(question_num: int, total: int, question: str, topic: str, q_type: str, difficulty: str):
    """Log a generated question with metadata."""
    diff_colors = {"easy": "green", "medium": "yellow", "hard": "red"}
    diff_color = diff_colors.get(difficulty, "white")

    panel = Panel(
        f"[bold white]{question}[/]\n\n"
        f"[dim]Topic:[/] [cyan]{topic}[/]  |  "
        f"[dim]Type:[/] [magenta]{q_type}[/]  |  "
        f"[dim]Difficulty:[/] [{diff_color}]{difficulty.upper()}[/{diff_color}]",
        title=f"[bold yellow]QUESTION {question_num}/{total}[/]",
        border_style="yellow",
        width=100,
    )
    console.print(panel)


def log_answer_received(answer: str):
    """Log candidate's answer."""
    preview = answer[:300] + ("..." if len(answer) > 300 else "")
    panel = Panel(
        f"[white]{preview}[/]",
        title="[bold blue]CANDIDATE ANSWER[/]",
        border_style="blue",
        width=100,
    )
    console.print(panel)


def log_evaluation(correctness: float, depth: float, clarity: float, overall: float, feedback: str):
    """Log evaluation scores and feedback."""
    def score_color(s):
        if s >= 8: return "bold green"
        if s >= 6: return "bold cyan"
        if s >= 4: return "bold yellow"
        return "bold red"

    scores_text = (
        f"  Correctness: [{score_color(correctness)}]{correctness}/10[/]  |  "
        f"  Depth: [{score_color(depth)}]{depth}/10[/]  |  "
        f"  Clarity: [{score_color(clarity)}]{clarity}/10[/]  |  "
        f"  [bold]Overall: [{score_color(overall)}]{overall}/10[/][/]"
    )

    panel = Panel(
        f"{scores_text}\n\n[dim]Feedback:[/] {feedback[:300]}",
        title="[bold green]EVALUATION[/]",
        border_style="green",
        width=100,
    )
    console.print(panel)


def log_full_context(context: str):
    """Log full retrieved context (truncated for readability)."""
    preview = context[:600] + ("..." if len(context) > 600 else "")
    panel = Panel(
        f"[dim]{preview}[/]",
        title="[bold magenta]FULL CONTEXT SENT TO LLM[/]",
        border_style="dim magenta",
        width=100,
    )
    console.print(panel)


def log_session_complete(session_id: int, total_questions: int, avg_score: float, recommendation: str):
    """Log interview completion summary."""
    rec_colors = {"strong_hire": "bold green", "hire": "bold cyan", "maybe": "bold yellow", "no_hire": "bold red"}
    rec_color = rec_colors.get(recommendation, "white")

    panel = Panel(
        f"[bold white]Session ID:[/] {session_id}\n"
        f"[bold white]Questions Answered:[/] {total_questions}\n"
        f"[bold white]Average Score:[/] [{rec_color}]{avg_score}/10[/]\n"
        f"[bold white]Recommendation:[/] [{rec_color}]{recommendation.upper().replace('_', ' ')}[/]",
        title="[bold green]INTERVIEW COMPLETE[/]",
        border_style="green",
        width=100,
    )
    console.print(panel)
    console.print()


def log_separator(label: str = ""):
    """Print a visual separator."""
    if label:
        console.rule(f"[bold dim]{label}[/]", style="dim")
    else:
        console.rule(style="dim")
