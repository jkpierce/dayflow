import subprocess


def start_tracking(task_description):
    """
    Start Timewarrior tracking for a task.
    Stops any currently running timer first.
    """

    stop_tracking()

    cmd = [
        "timew",
        "start",
        task_description
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            f"Failed to start tracking:\n{result.stderr}"
        )

    return result.stdout.strip()


def stop_tracking():
    """
    Stop current Timewarrior tracking session.
    Safe to call even if nothing is running.
    """

    cmd = [
        "timew",
        "stop"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    # Timewarrior returns non-zero if nothing active.
    # Ignore that case.

    return result.stdout.strip()


def get_active_tracking():
    """
    Returns currently tracked task text,
    or None if nothing is active.
    """

    cmd = [
        "timew",
        "get",
        "dom.active.tag"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    active = result.stdout.strip()

    if active == "":
        return None

    return active


def is_tracking():
    """
    Returns True if Timewarrior is active.
    """

    cmd = [
        "timew"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    output = result.stdout.lower()

    return "tracking" in output


def get_current_elapsed():
    """
    Returns elapsed tracked time for current task.
    Example:
        "0:32:14"
    """

    cmd = [
        "timew"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    for line in lines:

        if "Total" in line:
            return line.strip()

    return None
