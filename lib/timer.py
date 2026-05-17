import time
import signal
import sys
import select
import termios
import tty


class TimerInterrupted(Exception):
    pass


class DayflowAborted(Exception):
    """Raised when user presses q to quit everything."""
    pass


paused = False
pause_start_time = 0
total_paused_duration = 0


def signal_handler(sig, frame):
    raise TimerInterrupted


signal.signal(signal.SIGINT, signal_handler)


def _check_keypress():
    """
    Check for a single keypress without blocking.
    Returns the character pressed, or None.
    """
    if not sys.stdin.isatty():
        return None

    # Check if data is available on stdin
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)

    return None


def setup_terminal():
    """Set stdin to raw mode for single-key reading. Returns old settings."""
    if not sys.stdin.isatty():
        return None
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old


def restore_terminal(old):
    """Restore terminal to previous settings."""
    if old is not None and sys.stdin.isatty():
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def parse_estimate(estimate_str):
    """
    Convert Taskwarrior estimate strings into seconds.

    Supports both ISO 8601 duration format (PT1M, PT30S, PT1H30M)
    and legacy formats (30min, 90min, 1h, 2h, 1h30min, 30sec).
    """

    estimate_str = estimate_str.strip()

    # ISO 8601 duration format: PT1H30M, PT1M, PT30S, etc.
    if estimate_str.startswith("P") or estimate_str.startswith("p"):

        s = estimate_str.upper()

        # Remove the leading 'P' and 'T' prefix
        if "T" in s:
            s = s.split("T")[1]
        else:
            s = s[1:]  # shouldn't happen for durations

        total_seconds = 0
        num = ""

        for ch in s:

            if ch.isdigit():
                num += ch
            else:
                if num:

                    val = int(num)

                    if ch == "H":
                        total_seconds += val * 3600
                    elif ch == "M":
                        total_seconds += val * 60
                    elif ch == "S":
                        total_seconds += val

                    num = ""

        return total_seconds

    # Legacy format handling
    estimate_str = estimate_str.lower().strip()

    total_seconds = 0

    if "h" in estimate_str:

        hours_part = estimate_str.split("h")[0]

        if hours_part:
            total_seconds += int(hours_part) * 3600

        remainder = estimate_str.split("h")[1]

        if "min" in remainder:

            mins = remainder.replace("min", "")

            if mins:
                total_seconds += int(mins) * 60

    elif "min" in estimate_str:

        mins = estimate_str.replace("min", "")

        total_seconds += int(mins) * 60

    elif "sec" in estimate_str:

        secs = estimate_str.replace("sec", "")

        total_seconds += int(secs)

    return total_seconds


def format_seconds(seconds):
    """
    Convert seconds into HH:MM:SS
    """

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"


def countdown(duration_seconds, tick_callback=None):
    """
    Main countdown loop.

    tick_callback(elapsed, remaining)
        optional callback every second
    """

    global paused, pause_start_time, total_paused_duration

    start_time = time.time()
    total_paused_duration = 0
    remaining = duration_seconds
    elapsed = 0

    try:

        while elapsed < duration_seconds:

            # Check for keyboard input
            key = _check_keypress()

            if key == "p" or key == "P":
                if paused:
                    resume_timer()
                else:
                    pause_timer()
            elif key == "q" or key == "Q":
                raise DayflowAborted

            if paused:

                if pause_start_time == 0:
                    pause_start_time = time.time()

                if tick_callback:
                    tick_callback(elapsed, remaining, paused=True)

                time.sleep(0.2)
                continue

            if pause_start_time != 0:

                total_paused_duration += time.time() - pause_start_time
                pause_start_time = 0

            elapsed = int(
                time.time() - start_time - total_paused_duration
            )

            remaining = duration_seconds - elapsed

            if remaining < 0:
                remaining = 0

            if tick_callback:
                tick_callback(elapsed, remaining)

            time.sleep(0.2)

    except TimerInterrupted:
        return False

    return True


def pause_timer():
    global paused, pause_start_time
    if not paused:
        pause_start_time = time.time()
    paused = True


def resume_timer():
    global paused, pause_start_time, total_paused_duration
    if paused and pause_start_time != 0:
        total_paused_duration += time.time() - pause_start_time
        pause_start_time = 0
    paused = False


def is_paused():
    return paused
