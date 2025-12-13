from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
    CONFIG_FILE,
    AUDIT_FILE,
)
from srl.utils import today
import json
from pathlib import Path
from datetime import datetime


def add_subparser(subparsers):
    parser = subparsers.add_parser("import", help="Import learning progress data")
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Import file path (e.g., backup.json)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing data (default: replace)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without making changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    try:
        import_path = Path(args.file)
        
        # Validate import file
        if not import_path.exists():
            console.print(f"[bold red]Error:[/bold red] File {args.file} not found")
            return
            
        # Load import data
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        # Validate import format
        if not validate_import_data(import_data, console):
            return
            
        # Show import preview
        show_import_preview(import_data, console)
        
        if args.dry_run:
            console.print("[yellow]Dry run complete - no changes made.[/yellow]")
            return
            
        # Confirm import unless forced
        if not args.force:
            merge_text = "merge with" if args.merge else "replace"
            if not Confirm.ask(f"Do you want to {merge_text} your existing data?"):
                console.print("[yellow]Import cancelled.[/yellow]")
                return
        
        # Perform import
        imported_counts = perform_import(import_data, args.merge, console)
        
        # Show success message
        show_import_success(imported_counts, args.merge, console)
        
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Invalid JSON file:[/bold red] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Import failed:[/bold red] {str(e)}")


def validate_import_data(import_data: dict, console: Console) -> bool:
    """Validate the structure of import data."""
    required_keys = ["exported_at", "srl_version", "data"]
    
    for key in required_keys:
        if key not in import_data:
            console.print(f"[bold red]Invalid import file:[/bold red] Missing '{key}' field")
            return False
    
    if not isinstance(import_data["data"], dict):
        console.print(f"[bold red]Invalid import file:[/bold red] 'data' must be an object")
        return False
        
    return True


def show_import_preview(import_data: dict, console: Console):
    """Show what will be imported."""
    data = import_data["data"]
    export_type = import_data.get("export_type", "unknown")
    exported_at = import_data.get("exported_at", "unknown")
    
    preview_lines = []
    preview_lines.append(f"[bold]Export Date:[/bold] {exported_at}")
    preview_lines.append(f"[bold]Export Type:[/bold] {export_type}")
    preview_lines.append("")
    
    if "problems_in_progress" in data:
        count = len(data["problems_in_progress"])
        preview_lines.append(f"• {count} problems in progress")
        
    if "problems_mastered" in data:
        count = len(data["problems_mastered"])
        preview_lines.append(f"• {count} mastered problems")
        
    if "next_up" in data:
        count = len(data["next_up"])
        preview_lines.append(f"• {count} problems in next-up queue")
        
    if "config" in data:
        preview_lines.append("• Configuration settings")
        
    if "audit" in data:
        audit_history = data["audit"].get("history", [])
        preview_lines.append(f"• Audit history ({len(audit_history)} entries)")
    
    console.print(
        Panel.fit(
            "\n".join(preview_lines),
            title="[bold blue]Import Preview[/bold blue]",
            border_style="blue",
            title_align="left",
        )
    )


def perform_import(import_data: dict, merge: bool, console: Console) -> dict:
    """Perform the actual import operation."""
    data = import_data["data"]
    counts = {}
    
    # Import progress data
    if "problems_in_progress" in data:
        counts["progress"] = import_progress_data(data["problems_in_progress"], merge)
        
    # Import mastered data  
    if "problems_mastered" in data:
        counts["mastered"] = import_mastered_data(data["problems_mastered"], merge)
        
    # Import next-up data
    if "next_up" in data:
        counts["nextup"] = import_nextup_data(data["next_up"], merge)
        
    # Import config data
    if "config" in data:
        counts["config"] = import_config_data(data["config"], merge)
        
    # Import audit data
    if "audit" in data:
        counts["audit"] = import_audit_data(data["audit"], merge)
    
    return counts


def import_progress_data(import_progress: dict, merge: bool) -> int:
    """Import problems in progress."""
    if merge:
        existing = load_json(PROGRESS_FILE)
        existing.update(import_progress)
        save_json(PROGRESS_FILE, existing)
    else:
        save_json(PROGRESS_FILE, import_progress)
    
    return len(import_progress)


def import_mastered_data(import_mastered: dict, merge: bool) -> int:
    """Import mastered problems."""
    if merge:
        existing = load_json(MASTERED_FILE)
        existing.update(import_mastered)
        save_json(MASTERED_FILE, existing)
    else:
        save_json(MASTERED_FILE, import_mastered)
    
    return len(import_mastered)


def import_nextup_data(import_nextup: dict, merge: bool) -> int:
    """Import next-up problems."""
    if merge:
        existing = load_json(NEXT_UP_FILE)
        existing.update(import_nextup)
        save_json(NEXT_UP_FILE, existing)
    else:
        save_json(NEXT_UP_FILE, import_nextup)
    
    return len(import_nextup)


def import_config_data(import_config: dict, merge: bool) -> int:
    """Import configuration."""
    if merge:
        existing = load_json(CONFIG_FILE)
        existing.update(import_config)
        save_json(CONFIG_FILE, existing)
    else:
        save_json(CONFIG_FILE, import_config)
    
    return 1 if import_config else 0


def import_audit_data(import_audit: dict, merge: bool) -> int:
    """Import audit history."""
    if merge:
        existing = load_json(AUDIT_FILE)
        # Merge audit history arrays
        existing_history = existing.get("history", [])
        import_history = import_audit.get("history", [])
        
        # Combine histories and remove duplicates based on date+problem
        combined_history = existing_history + import_history
        seen = set()
        unique_history = []
        
        for entry in combined_history:
            key = (entry.get("date", ""), entry.get("problem", ""))
            if key not in seen:
                seen.add(key)
                unique_history.append(entry)
        
        existing["history"] = unique_history
        
        # Update other audit fields
        for key, value in import_audit.items():
            if key != "history":
                existing[key] = value
                
        save_json(AUDIT_FILE, existing)
    else:
        save_json(AUDIT_FILE, import_audit)
    
    return len(import_audit.get("history", []))


def show_import_success(counts: dict, merge: bool, console: Console):
    """Show successful import summary."""
    operation = "merged" if merge else "imported"
    success_lines = []
    
    if "progress" in counts:
        success_lines.append(f"• {counts['progress']} problems in progress {operation}")
        
    if "mastered" in counts:
        success_lines.append(f"• {counts['mastered']} mastered problems {operation}")
        
    if "nextup" in counts:
        success_lines.append(f"• {counts['nextup']} next-up problems {operation}")
        
    if "config" in counts and counts["config"]:
        success_lines.append(f"• Configuration settings {operation}")
        
    if "audit" in counts:
        success_lines.append(f"• {counts['audit']} audit entries {operation}")
    
    if not success_lines:
        success_lines.append("No data was imported")
    
    console.print(
        Panel.fit(
            f"[green]✓[/green] Import completed successfully!\n\n" +
            "\n".join(success_lines),
            title="[bold green]Import Complete[/bold green]",
            border_style="green",
            title_align="left",
        )
    )