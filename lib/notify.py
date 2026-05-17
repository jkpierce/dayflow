import time
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SOUND_DIR = BASE_DIR / "sounds"

DEFAULT_SOUND = SOUND_DIR / "alarm.oga"


def send_notification(
    title,
    message="",
    urgency="normal",
    timeout=2000
):
    """
    Send desktop notification using notify-send.

    urgency:
        low
        normal
        critical

    timeout:
        milliseconds
    """

    cmd = [
        "notify-send",
        "-a", "Dayflow",
        "-u",
        urgency,
        "-t", str(timeout),
        "-p",
        title,
        message
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    notif_id = result.stdout.strip()

    # GNOME ignores -t, so force-close after the timeout via dbus
    if notif_id.isdigit():
        close_delay = max(timeout // 1000, 1)
        subprocess.Popen(
            ["bash", "-c",
             f"sleep {close_delay} && "
             f"gdbus call --session "
             f"--dest org.freedesktop.Notifications "
             f"--object-path /org/freedesktop/Notifications "
             f"--method org.freedesktop.Notifications.CloseNotification "
             f"{notif_id} >/dev/null 2>&1"]
        )


def play_sound(sound_file=None):
    """
    Play notification sound using paplay.
    A tiny delay prevents the start of the sound from getting clipped.
    """

    if sound_file is None:
        sound_file = DEFAULT_SOUND

    sound_file = str(sound_file)

    time.sleep(0.15)

    cmd = [
        "paplay",
        sound_file
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def alert(
    title,
    message="",
    urgency="critical",
    sound=True
):
    """
    Combined notification + sound.
    """

    send_notification(
        title=title,
        message=message,
        urgency=urgency
    )

    if sound:
        play_sound()


def fullscreen_alert(message):
    """
    Interruptive fullscreen popup using zenity.
    """

    cmd = [
        "zenity",
        "--warning",
        "--title=Dayflow",
        f"--text={message}",
        "--width=400",
        "--height=200"
    ]

    subprocess.run(cmd)


def voice_alert(message):
    """
    Text-to-speech alert.
    Requires:
        sudo apt install speech-dispatcher
    """

    cmd = [
        "spd-say",
        message
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
