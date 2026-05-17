# Dayflow

A task-timer that reads tasks from a text file, tracks them with **Taskwarrior** + **Timewarrior**, and notifies you with desktop popups and sounds at each task transition.

## Features

- **Reads tasks from a plain text file** — no manual taskwarrior commands needed
- **Live terminal dashboard** — shows current task, elapsed/remaining time, and upcoming queue
- **Desktop notifications** — combined popup at each transition shows what finished and what's next
- **Sound alerts** — Star Trek computer alarm plays when a task completes
- **Keyboard controls** — `p` to pause/resume, `q` to quit
- **Auto-advance** — tasks run one after the other automatically
- **Time tracking** — time is logged in Timewarrior

## Dependencies

```bash
sudo apt install taskwarrior timewarrior libnotify-bin pulseaudio-utils zenity python3-pip jq
pip install rich
```

Configure Taskwarrior's estimate field (if not already set):

```bash
task config uda.estimate.type duration
task config uda.estimate.label estimate
```

## Installation

```bash
git clone https://github.com/jkpierce/dayflow.git ~/dayflow
cd ~/dayflow
```

## Usage

### 1. Write your tasks

Edit `tasks.txt`:

```
# Dayflow Task List
# Format: estimate | task description

30min | Write documentation
1h    | Review pull requests
15min | Check email
```

Supported estimates: `30min`, `1h`, `1h30min`, `15min`, `30sec`, `10s`, etc.

### 2. Run it

```bash
cd ~/dayflow
./start.sh
```

### What happens

1. A "Starting Dayflow" popup shows the first task
2. Each task runs through its countdown on the live dashboard
3. At each transition: a combined notification pops up (with sound) showing what finished and what's next
4. After the last task: a quiet "Sequence Complete" popup appears

### Keyboard controls (during a task)

| Key | Action |
|-----|--------|
| `p` | Pause / resume the timer |
| `q` | Abort the entire sequence |

### What happens to Taskwarrior?

- Tasks are marked **completed** as you finish them
- Tracked time is saved in **Timewarrior** (`timew summary` to view)
- No stale tasks left behind after a run

### Custom sounds

Replace `sounds/alarm.oga` with any `.oga` file to change the alert sound.
