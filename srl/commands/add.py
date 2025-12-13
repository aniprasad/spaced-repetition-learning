from rich.console import Console
from srl.utils import today
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)
from srl.commands.list_ import get_due_problems


def add_subparser(subparsers):
    add = subparsers.add_parser("add", help="Add or update a problem attempt")
    group = add.add_mutually_exclusive_group(required=True)
    group.add_argument("name", nargs="?", type=str, help="Name of the problem")
    group.add_argument(
        "-n", "--number", type=int, help="Problem number from `srl list`"
    )
    group.add_argument(
        "--leetcode-id", type=int, help="LeetCode problem ID to add/update"
    )
    add.add_argument("rating", type=int, choices=range(1, 6), help="Rating from 1-5")
    add.add_argument(
        "--id", type=int, help="Optional LeetCode problem ID (when adding by name)"
    )
    add.add_argument(
        "--note", type=str, help="Note about the solution/approach"
    )
    add.add_argument(
        "--mistake", type=str, help="What went wrong or what to watch out for"
    )
    add.add_argument(
        "--time", type=int, help="Time spent in minutes"
    )
    add.set_defaults(handler=handle)
    return add


def handle(args, console: Console):
    rating: int = args.rating
    leetcode_id = getattr(args, "id", None)
    
    if hasattr(args, "leetcode_id") and args.leetcode_id is not None:
        # Search by LeetCode ID
        data = load_json(PROGRESS_FILE)
        name = None
        for key, value in data.items():
            if value.get("leetcode_id") == args.leetcode_id:
                name = key
                break
        
        if not name:
            # Check mastered as well
            mastered = load_json(MASTERED_FILE)
            for key, value in mastered.items():
                if value.get("leetcode_id") == args.leetcode_id:
                    console.print(
                        f"[bold red]Problem with LeetCode ID {args.leetcode_id} is already mastered.[/bold red]"
                    )
                    return
            
            console.print(
                f"[bold red]No problem found with LeetCode ID {args.leetcode_id}.[/bold red]"
            )
            console.print(
                "[yellow]Hint:[/yellow] Add a new problem first with: srl add \"Problem Name\" --id {args.leetcode_id} <rating>"
            )
            return
    elif hasattr(args, "number") and args.number is not None:
        problems = get_due_problems()
        if args.number > len(problems) or args.number <= 0:
            console.print(f"[bold red]Invalid problem number: {args.number}[/bold red]")
            return
        name = problems[args.number - 1]
    else:
        name: str = args.name

    data = load_json(PROGRESS_FILE)

    # Check for existing entry case-insensitively
    existing_name = None
    for key in data:
        if key.lower() == name.lower():
            existing_name = key
            break

    # Use existing name if found, otherwise use the provided name
    target_name = existing_name if existing_name else name
    entry = data.get(target_name, {"history": []})
    
    # Add or update LeetCode ID if provided
    if leetcode_id is not None:
        entry["leetcode_id"] = leetcode_id
    
    # Build history entry
    history_entry = {
        "rating": rating,
        "date": today().isoformat(),
    }
    
    # Add optional fields if provided
    if hasattr(args, "note") and args.note:
        history_entry["note"] = args.note
    if hasattr(args, "mistake") and args.mistake:
        history_entry["mistake"] = args.mistake
    if hasattr(args, "time") and args.time:
        history_entry["time_spent"] = args.time
    
    entry["history"].append(history_entry)

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        if target_name in mastered:
            mastered[target_name]["history"].extend(history)
        else:
            mastered[target_name] = entry
        save_json(MASTERED_FILE, mastered)
        if target_name in data:
            del data[target_name]
        console.print(
            f"[bold green]{target_name}[/bold green] moved to [cyan]mastered[/cyan]!"
        )
    else:
        data[target_name] = entry
        console.print(
            f"Added rating [yellow]{rating}[/yellow] for '[cyan]{target_name}[/cyan]'"
        )

    save_json(PROGRESS_FILE, data)

    # Remove from next up if it exists there
    next_up = load_json(NEXT_UP_FILE)
    if target_name in next_up:
        del next_up[target_name]
        save_json(NEXT_UP_FILE, next_up)
