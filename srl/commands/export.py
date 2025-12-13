from rich.console import Console
from rich.panel import Panel
from srl.storage import (
    load_json,
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
    parser = subparsers.add_parser("export", help="Export your learning progress data")
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path (e.g., backup.json)",
    )
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="Include configuration settings in export",
    )
    parser.add_argument(
        "--include-audit",
        action="store_true", 
        help="Include audit history in export",
    )
    parser.add_argument(
        "--mastered-only",
        action="store_true",
        help="Export only mastered problems",
    )
    parser.add_argument(
        "--progress-only",
        action="store_true",
        help="Export only problems in progress",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    try:
        output_path = Path(args.output)
        
        # Validate output path
        if output_path.exists():
            console.print(f"[yellow]Warning: File {args.output} already exists and will be overwritten.[/yellow]")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load data
        progress_data = load_json(PROGRESS_FILE)
        mastered_data = load_json(MASTERED_FILE)
        nextup_data = load_json(NEXT_UP_FILE)
        
        # Build export data based on flags
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "srl_version": "1.0.0",
            "export_type": "full",
            "data": {}
        }
        
        if args.mastered_only:
            export_data["export_type"] = "mastered_only"
            export_data["data"]["problems_mastered"] = mastered_data
        elif args.progress_only:
            export_data["export_type"] = "progress_only"
            export_data["data"]["problems_in_progress"] = progress_data
        else:
            # Full export
            export_data["data"]["problems_in_progress"] = progress_data
            export_data["data"]["problems_mastered"] = mastered_data
            export_data["data"]["next_up"] = nextup_data
        
        # Optional data
        if args.include_config:
            config_data = load_json(CONFIG_FILE)
            export_data["data"]["config"] = config_data
            
        if args.include_audit:
            audit_data = load_json(AUDIT_FILE)
            export_data["data"]["audit"] = audit_data
        
        # Write export file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Generate summary
        summary_lines = []
        if "problems_in_progress" in export_data["data"]:
            progress_count = len(progress_data)
            summary_lines.append(f"• {progress_count} problems in progress")
        
        if "problems_mastered" in export_data["data"]:
            mastered_count = len(mastered_data)
            summary_lines.append(f"• {mastered_count} mastered problems")
            
        if "next_up" in export_data["data"]:
            nextup_count = len(nextup_data)
            summary_lines.append(f"• {nextup_count} problems in next-up queue")
            
        if args.include_config:
            summary_lines.append("• Configuration settings")
            
        if args.include_audit:
            summary_lines.append("• Audit history")
        
        # Display success message
        file_size = output_path.stat().st_size
        file_size_str = f"{file_size:,} bytes"
        
        summary_text = "\n".join(summary_lines) if summary_lines else "No data exported"
        
        console.print(
            Panel.fit(
                f"[green]✓[/green] Export completed successfully!\n\n"
                f"[bold]File:[/bold] {args.output}\n"
                f"[bold]Size:[/bold] {file_size_str}\n"
                f"[bold]Type:[/bold] {export_data['export_type']}\n\n"
                f"[bold]Exported:[/bold]\n{summary_text}",
                title="[bold green]Export Complete[/bold green]",
                border_style="green",
                title_align="left",
            )
        )
        
        # Usage tip
        console.print(
            f"\n[dim]💡 To import this data elsewhere, use:[/dim] [cyan]srl import -f {args.output}[/cyan]"
        )
        
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {str(e)}")