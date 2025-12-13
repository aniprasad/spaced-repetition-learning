from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from srl.storage import load_json, PROGRESS_FILE, MASTERED_FILE
from srl.commands.list_ import get_due_problems
from datetime import datetime, timedelta
from srl.utils import today


def add_subparser(subparsers):
    parser = subparsers.add_parser("show", help="Show problem history and notes")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("name", nargs="?", type=str, help="Name of the problem")
    group.add_argument(
        "-n", "--number", type=int, help="Problem number from `srl list`"
    )
    group.add_argument(
        "--leetcode-id", type=int, help="LeetCode problem ID"
    )
    parser.add_argument(
        "--compact", action="store_true", help="Show compact view with notes/mistakes/time only"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    # Determine problem name
    if hasattr(args, "leetcode_id") and args.leetcode_id is not None:
        name = find_by_leetcode_id(args.leetcode_id)
        if not name:
            console.print(
                f"[bold red]No problem found with LeetCode ID {args.leetcode_id}[/bold red]"
            )
            return
    elif hasattr(args, "number") and args.number is not None:
        problems = get_due_problems()
        if args.number > len(problems) or args.number <= 0:
            console.print(f"[bold red]Invalid problem number: {args.number}[/bold red]")
            return
        name = problems[args.number - 1]
    else:
        name = args.name

    # Find problem in progress or mastered
    progress_data = load_json(PROGRESS_FILE)
    mastered_data = load_json(MASTERED_FILE)
    
    problem_data = None
    status = None
    
    # Check case-insensitively
    for key in progress_data:
        if key.lower() == name.lower():
            problem_data = progress_data[key]
            status = "In Progress"
            name = key  # Use the actual stored name
            break
    
    if not problem_data:
        for key in mastered_data:
            if key.lower() == name.lower():
                problem_data = mastered_data[key]
                status = "Mastered"
                name = key
                break
    
    if not problem_data:
        console.print(f"[bold red]Problem '{name}' not found[/bold red]")
        return
    
    # Display problem header
    leetcode_id = problem_data.get("leetcode_id", "")
    header = f"Problem: {name}"
    if leetcode_id:
        header += f" (#{leetcode_id})"
    
    console.print()
    console.print(f"[bold cyan]{header}[/bold cyan]")
    console.print(f"Status: [{'green' if status == 'Mastered' else 'yellow'}]{status}[/{'green' if status == 'Mastered' else 'yellow'}]")
    
    # Calculate next review date if in progress
    if status == "In Progress":
        history = problem_data.get("history", [])
        if history:
            last_entry = history[-1]
            last_date = datetime.fromisoformat(last_entry["date"]).date()
            next_date = last_date + timedelta(days=last_entry["rating"])
            days_until = (next_date - today()).days
            
            if days_until > 0:
                console.print(f"Next Review: [cyan]{next_date.isoformat()}[/cyan] (in {days_until} day{'s' if days_until != 1 else ''})")
            elif days_until == 0:
                console.print(f"Next Review: [yellow]Today[/yellow]")
            else:
                console.print(f"Next Review: [red]Overdue by {abs(days_until)} day{'s' if abs(days_until) != 1 else ''}[/red]")
    
    console.print()
    
    # Create table for history
    history = problem_data.get("history", [])
    if not history:
        console.print("[yellow]No history available[/yellow]")
        return
    
    # Compact view
    if hasattr(args, "compact") and args.compact:
        console.print(f"[bold dim]Showing attempts with notes/mistakes only[/bold dim]")
        console.print()
        
        last_date = None
        attempts_with_notes = []
        
        # First pass: collect attempts with notes/mistakes and track original indices
        for i, entry in enumerate(history, 1):
            if entry.get("note") or entry.get("mistake"):
                attempts_with_notes.append((i, entry))
        
        if not attempts_with_notes:
            console.print("[dim]No attempts with notes or mistakes to show[/dim]")
            console.print()
            return
            
        for original_idx, entry in attempts_with_notes:
            current_date = entry["date"]
            
            # Show date separator with improved styling
            if current_date != last_date:
                if last_date is not None:
                    console.print()
                # Make date more readable
                try:
                    date_obj = datetime.fromisoformat(current_date)
                    formatted_date = date_obj.strftime("%b %d, %Y")
                except:
                    formatted_date = current_date
                console.print(f"[bold blue]📅 {formatted_date}[/bold blue]")
                last_date = current_date
            
            # Build attempt header with better spacing
            rating_stars = "⭐" * entry["rating"]
            time_str = f"⏱️ {entry.get('time_spent', '')}m" if entry.get('time_spent') else ""
            
            # Progress indicator based on rating
            if entry["rating"] >= 5:
                progress_emoji = "🎯"
            elif entry["rating"] >= 4:
                progress_emoji = "✅"
            elif entry["rating"] >= 3:
                progress_emoji = "⚡"
            else:
                progress_emoji = "📝"
                
            header_line = f"  {progress_emoji} [dim]#{original_idx}[/dim] {rating_stars}"
            if time_str:
                header_line += f" [magenta]{time_str}[/magenta]"
                
            console.print(header_line)
            
            # Show note with proper text wrapping
            if entry.get("note"):
                note_text = entry["note"]
                console.print(f"    [dim]💡 [/dim][white]{note_text}[/white]")
                
            # Show mistake with distinct styling
            if entry.get("mistake"):
                mistake_text = entry["mistake"]
                console.print(f"    [dim]⚠️  [/dim][red]{mistake_text}[/red]")
            
            # Add small spacing between attempts on same date
            console.print()
        
        # Show summary stats
        total_attempts = len(history)
        attempts_with_data = len(attempts_with_notes)
        avg_rating = sum(e["rating"] for e in history) / len(history) if history else 0
        
        console.print(f"[dim]📊 Showing {attempts_with_data}/{total_attempts} attempts • Average rating: {avg_rating:.1f}⭐[/dim]")
        console.print()
        return
    
    # Full table view
    table = Table(title=f"Attempt History ({len(history)})", title_justify="left")
    table.add_column("#", style="dim", no_wrap=True)
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Rating", no_wrap=True)
    table.add_column("Time", style="magenta", no_wrap=True)
    table.add_column("Note", style="white")
    table.add_column("Mistake", style="red")
    
    for i, entry in enumerate(history, 1):
        rating_stars = "⭐" * entry["rating"]
        time_str = f"{entry.get('time_spent', '')}m" if entry.get('time_spent') else "-"
        note_str = entry.get("note", "-")
        mistake_str = entry.get("mistake", "-")
        
        table.add_row(
            str(i),
            entry["date"],
            rating_stars,
            time_str,
            note_str,
            mistake_str
        )
    
    console.print(table)
    console.print()


def find_by_leetcode_id(leetcode_id):
    """Find problem name by LeetCode ID in progress or mastered"""
    progress_data = load_json(PROGRESS_FILE)
    for name, data in progress_data.items():
        if data.get("leetcode_id") == leetcode_id:
            return name
    
    mastered_data = load_json(MASTERED_FILE)
    for name, data in mastered_data.items():
        if data.get("leetcode_id") == leetcode_id:
            return name
    
    return None
