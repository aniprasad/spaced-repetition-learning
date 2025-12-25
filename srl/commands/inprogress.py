from rich.console import Console
from rich.panel import Panel
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)
from srl.commands.list_ import maybe_trigger_audit


def add_subparser(subparsers):
    parser = subparsers.add_parser("inprogress", help="List problems in progress")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    if maybe_trigger_audit(console):
        return

    data = load_json(PROGRESS_FILE)
    in_progress = get_in_progress()
    if in_progress:
        lines = []
        for i, p in enumerate(in_progress):
            leetcode_id = ""
            if p in data and "leetcode_id" in data[p]:
                leetcode_id = f"[dim]#{data[p]['leetcode_id']}[/dim] "
            lines.append(f"{i+1}. {leetcode_id}{p}")
        
        console.print(
            Panel.fit(
                "\n".join(lines),
                title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
                border_style="magenta",
                title_align="left",
            )
        )
    else:
        console.print("[yellow]No problems currently in progress.[/yellow]")


def get_in_progress() -> list[str]:
    data = load_json(PROGRESS_FILE)
    res = []

    for name, _ in data.items():
        res.append(name)

    return res
