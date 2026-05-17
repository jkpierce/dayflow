from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.align import Align

from lib.tasks import (
    get_pending_tasks,
    mark_done
)

from lib.tracker import (
    start_tracking,
    stop_tracking
)

from lib.notify import (
    alert,
    send_notification
)

from lib.timer import (
    parse_estimate,
    format_seconds,
    countdown,
    DayflowAborted,
    setup_terminal,
    restore_terminal
)

import time


console = Console()


def build_dashboard(
    current_task,
    elapsed,
    remaining,
    queue,
    paused=False
):

    table = Table.grid(expand=True)

    if paused:
        status = "⏸  PAUSED"
        status_style = "bold yellow"
    else:
        status = "ACTIVE"
        status_style = "bold green"

    panel_text = f"""
[bold cyan]{current_task}[/bold cyan]

Status: [{status_style}]{status}[/{status_style}]

Elapsed:  {format_seconds(elapsed)}
Remaining: {format_seconds(remaining)}
"""

    table.add_row(
        Panel(
            Align.center(panel_text),
            title="Dayflow",
            border_style="green"
        )
    )

    if queue:

        queue_text = "\n".join(
            f"- {task['description']} ({task['estimate']})"
            for task in queue[:5]
        )

    else:
        queue_text = "No remaining tasks"

    table.add_row(
        Panel(
            queue_text,
            title="Upcoming",
            border_style="blue"
        )
    )

    return table


def run_task(task, remaining_tasks, next_task, live):
    """Run a single task within an existing Live context."""

    task_id = task["id"]
    description = task["description"]
    estimate = task["estimate"]

    duration_seconds = parse_estimate(estimate)

    start_tracking(description)

    # Show the new task immediately
    live.update(
        build_dashboard(
            description,
            0,
            duration_seconds,
            remaining_tasks
        )
    )

    def live_tick(elapsed, remaining, **kwargs):

        live.update(
            build_dashboard(
                description,
                elapsed,
                remaining,
                remaining_tasks,
                paused=kwargs.get("paused", False)
            )
        )

    completed = countdown(
        duration_seconds,
        live_tick
    )

    if not completed:

        stop_tracking()

        return

    # Single transition notification: done + what's next
    if next_task:
        msg = (
            f"✓ {description}\n"
            f"\n"
            f"→ Next: {next_task['description']} ({next_task['estimate']})"
        )
    else:
        msg = f"✓ {description}\n\nThat was the last task."

    alert(
        "Task Complete",
        msg,
        urgency="normal"
    )

    stop_tracking()

    mark_done(task_id)


def main():

    console.print(
        "\n[bold green]Starting Dayflow...[/bold green]\n"
    )

    console.print(
        "[dim]Press [bold]p[/bold] to pause  [bold]q[/bold] to quit[/dim]"
    )
    console.print()

    tasks = get_pending_tasks()

    if not tasks:

        console.print(
            "[bold red]No pending +today tasks found.[/bold red]"
        )

        return

    # Static task list — stays visible above the live dashboard
    console.print("[bold]Today's Tasks:[/bold]")
    for t in tasks:
        console.print(f"  • {t['description']} ({t['estimate']})")
    console.print()

    old = setup_terminal()

    try:

        send_notification(
            "Starting Dayflow",
            f"First up: {tasks[0]['description']} ({tasks[0]['estimate']})",
            urgency="normal"
        )

        with Live(
            build_dashboard(
                tasks[0]["description"],
                0,
                parse_estimate(tasks[0]["estimate"]),
                tasks[1:]
            ),
            refresh_per_second=4,
            console=console
        ) as live:

            for index, task in enumerate(tasks):

                remaining_tasks = tasks[index + 1:]
                next_task = tasks[index + 1] if index + 1 < len(tasks) else None

                run_task(task, remaining_tasks, next_task, live)

        # Brief pause so the last task's completion sound finishes
        time.sleep(2)

        send_notification(
            "Sequence Complete",
            "All scheduled tasks finished",
            urgency="normal"
        )

        console.print(
            "\n[bold cyan]Dayflow sequence complete.[/bold cyan]\n"
        )

    except DayflowAborted:

        stop_tracking()

        console.print(
            "\n[bold yellow]Dayflow aborted.[/bold yellow]\n"
        )

    finally:

        restore_terminal(old)


if __name__ == "__main__":

    try:

        main()

    except (KeyboardInterrupt, DayflowAborted):

        stop_tracking()

        console.print(
            "\n[bold yellow]Dayflow aborted.[/bold yellow]\n"
        )
