from rich.console import Console
from collections import Counter
from pathlib import Path
from datetime import date, timedelta
from rich.table import Table
from srl.storage import (
    load_json,
    MASTERED_FILE,
    PROGRESS_FILE,
    AUDIT_FILE,
)
from srl.commands.config import Config


def add_subparser(subparsers):
    parser = subparsers.add_parser("calendar", help="Graph of SRL activity")
    parser.add_argument(
        "-m",
        "--months",
        type=int,
        default=12,
        help="Number of months to display (default: 12)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show activity summary statistics",
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    colors = Config.load().calendar_colors
    counts = get_all_date_counts()
    render_activity(console, counts, colors, getattr(args, "months", 12))
    console.print("-" * 5)
    render_legend(console, colors)
    if getattr(args, "summary", False):
        render_summary(console, counts, getattr(args, "months", 12))


def render_legend(console: Console, colors: dict[int, str]):
    squares = " ".join(f"[{colors[level]}]■[/]" for level in colors)
    legend = f"Less {squares} More"
    console.print(legend)


def render_activity(
    console: Console,
    counts: Counter[str],
    colors: dict[int, str],
    months: int,
):
    today = date.today()
    months_list = []
    year = today.year
    month = today.month
    for _ in range(months):
        months_list.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    
    # Display the date range for the calendar
    start_year, start_month = months_list[-1]  # Earliest month
    end_year, end_month = months_list[0]       # Latest month
    
    start_date = date(start_year, start_month, 1)
    end_date = date(end_year, end_month, 1)
    
    start_str = start_date.strftime("%B %Y")
    end_str = end_date.strftime("%B %Y")
    
    if months == 1:
        # Single month
        console.print(f"[bold cyan]{start_str}[/bold cyan]")
    elif start_year == end_year:
        # Same year, show abbreviated format
        if start_month == end_month:
            console.print(f"[bold cyan]{start_str}[/bold cyan]")
        else:
            start_abbrev = start_date.strftime("%b")
            console.print(f"[bold cyan]{start_abbrev} - {end_str}[/bold cyan]")
    else:
        # Different years, show full format
        console.print(f"[bold cyan]{start_str} - {end_str}[/bold cyan]")
    console.print()  # Add spacing after the header

    grids: list[list[list[int | str]]] = []
    for y, m in reversed(months_list):
        month_start = date(y, m, 1)
        grid = build_month(month_start, counts, today)
        grids.append(grid)

    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    default_color = list(colors.values())[-1]
    table = Table(
        show_header=False,
        show_edge=False,
        box=None,
        padding=(0, 0),
    )

    for row_idx in range(7):
        combined_row: list[int | str] = [days_of_week[row_idx], " "]
        for grid in grids:
            combined_row.extend(grid[row_idx])

        rendered_row = []
        for item in combined_row:
            if isinstance(item, int):
                rendered_row.append(f" [{colors.get(item, default_color)}]■[/]")
            elif isinstance(item, str) and item.startswith("TODAY:"):
                # Extract the count from TODAY:count
                count = int(item.split(":")[1])
                rendered_row.append(f" [{colors.get(count, default_color)}]⬜[/]")
            else:
                rendered_row.append(item)
        table.add_row(*rendered_row)

    console.print(table)


def key(d: date) -> str:
    return d.isoformat()


def render_summary(console: Console, counts: Counter[str], months: int):
    """Render activity summary statistics"""
    # Filter counts to only include dates within the specified month range
    today = date.today()
    months_list = []
    year = today.year
    month = today.month
    for _ in range(months):
        months_list.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    
    # Calculate the date range for filtering
    start_year, start_month = months_list[-1]  # Earliest month
    start_date = date(start_year, start_month, 1)
    end_date = today
    
    # Filter counts to only include dates within the month range
    filtered_counts = Counter()
    for date_str, count in counts.items():
        try:
            activity_date = date.fromisoformat(date_str)
            if start_date <= activity_date <= end_date:
                filtered_counts[date_str] = count
        except:
            continue  # Skip invalid date strings
    
    # Calculate summary stats from filtered data
    total_problems = sum(filtered_counts.values())
    total_days = len(filtered_counts)
    
    if total_problems == 0:
        console.print("[dim]No activity in this period[/dim]")
        return
    
    # Find most active day
    max_count = max(filtered_counts.values())
    most_active_days = [day for day, count in filtered_counts.items() if count == max_count]
    most_active_day = most_active_days[0]  # Just take the first if multiple
    
    # Calculate streak (consecutive days with activity) from filtered data
    sorted_days = sorted(filtered_counts.keys())
    current_streak = 0
    max_streak = 0
    
    for i, day_str in enumerate(sorted_days):
        day_date = date.fromisoformat(day_str)
        if i == 0:
            current_streak = 1
        else:
            prev_day_str = sorted_days[i-1]
            prev_date = date.fromisoformat(prev_day_str)
            if (day_date - prev_date).days == 1:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
    max_streak = max(max_streak, current_streak)
    
    # Format most active day
    try:
        active_date = date.fromisoformat(most_active_day)
        formatted_date = active_date.strftime("%b %d")
    except:
        formatted_date = most_active_day
    
    # Build and display summary with better formatting
    avg_per_active_day = total_problems / total_days if total_days > 0 else 0
    
    console.print()
    console.print("[bold]Activity Summary:[/bold]")
    console.print(f"  • [bold green]{total_problems}[/bold green] problems solved across [yellow]{total_days}[/yellow] active days")
    console.print(f"  • Average: [cyan]{avg_per_active_day:.1f}[/cyan] problems per active day")
    
    if max_streak > 1:
        console.print(f"  • Best streak: [magenta]{max_streak}[/magenta] consecutive days")
    
    if max_count > 1:
        console.print(f"  • Most active day: [bright_blue]{formatted_date}[/bright_blue] with [green]{max_count}[/green] problems")


def get_all_date_counts() -> Counter[str]:
    counts = Counter()
    counts.update(get_dates(MASTERED_FILE))
    counts.update(get_dates(PROGRESS_FILE))
    counts.update(get_audit_dates())

    return counts


def get_dates(path: Path) -> list[str]:
    json_data = load_json(path)
    res = []

    for obj in json_data.values():
        history = obj.get("history", [])
        if not history:
            continue
        for record in history:
            date = record.get("date", "")
            if date:
                res.append(date)

    return res


def get_audit_dates() -> list[str]:
    audit_data = load_json(AUDIT_FILE)
    history = audit_data.get("history", [])
    res = []

    for record in history:
        result = record.get("result", "")
        date = record.get("date", "")
        if date and result == "pass":
            res.append(date)

    return res


def build_month(
    month_start: date,
    counts: Counter[str],
    today: date,
) -> list[list[int | str]]:
    grid: list[list[int | str]] = [[" " for _ in range(8)] for _ in range(7)]

    current_month = month_start.month
    day = month_start

    col = 0
    while day.month == current_month and day <= today:
        row = (day.weekday() + 1) % 7
        count = counts.get(key(day), 0)
        # Mark today with special marker
        if day == today:
            grid[row][col] = f"TODAY:{count}"  # Special marker for today
        else:
            grid[row][col] = count
        day += timedelta(days=1)
        if row == 6:
            col += 1

    grid = remove_empty_columns(grid)
    return grid


def remove_empty_columns(grid) -> list[list[int | str]]:
    non_empty_cols = []
    num_cols = len(grid[0]) if grid else 0
    for col_idx in range(num_cols):
        if any(row[col_idx] != " " for row in grid):
            non_empty_cols.append(col_idx)

    new_grid = []
    for row in grid:
        new_row = [row[col_idx] for col_idx in non_empty_cols] + [" "]
        new_grid.append(new_row)

    return new_grid
