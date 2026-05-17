#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

TASKS_FILE="tasks.txt"

if [ ! -f "$TASKS_FILE" ]; then
    echo "Error: tasks.txt not found in $(pwd)"
    exit 1
fi

# Read tasks, skipping comments and blanks
tasks=()
while IFS= read -r line; do
    line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$line" || "$line" == \#* ]] && continue
    tasks+=("$line")
done < "$TASKS_FILE"

if [ ${#tasks[@]} -eq 0 ]; then
    echo "No tasks found in $TASKS_FILE" >&2
    exit 1
fi

# Clear any existing +today tasks silently
task +today status:pending export 2>/dev/null | python3 -c "
import json, sys, subprocess
try:
    data = json.load(sys.stdin)
    for t in data:
        tid = t.get('id')
        if tid:
            subprocess.run(['task', str(tid), 'delete', 'rc.confirmation=no'],
                         capture_output=True)
except:
    pass
" 2>/dev/null || true

# Add tasks to taskwarrior silently
for task in "${tasks[@]}"; do
    estimate="$(echo "$task" | sed 's/^[[:space:]]*\([^|]*\)[[:space:]]*|.*/\1/' | xargs)"
    desc="$(echo "$task" | sed 's/^[[:space:]]*[^|]*[[:space:]]*|[[:space:]]*\(.*\)/\1/' | xargs)"
    task add "$desc" estimate:"$estimate" +today > /dev/null
done

python -m lib.scheduler
