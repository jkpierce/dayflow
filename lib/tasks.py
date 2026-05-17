import json
import subprocess


def get_pending_tasks():
    """
    Fetch pending tasks tagged +today
    """

    cmd = [
        "task",
        "+today",
        "status:pending",
        "export"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    tasks = json.loads(result.stdout)

    parsed = []

    for task in tasks:

        estimate = task.get("estimate", "0min")

        parsed.append({
            "id": task["id"],
            "description": task["description"],
            "estimate": estimate
        })

    return parsed


def mark_done(task_id):

    subprocess.run(
        ["task", str(task_id), "done"],
        capture_output=True
    )
