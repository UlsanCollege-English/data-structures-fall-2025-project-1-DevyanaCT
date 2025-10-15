
# Multi-Queue Round-Robin Café (Interactive CLI)
This project mimics a café that uses a round-robin scheduling algorithm to process orders from several client queues, guaranteeing equity for all queues (e.g., Mobile, WalkIns, Faculty).
Every queue has it's own capacity, and every order (task) is assigned a task ID that increases automatically, such as Mobile-001

Features:
Make several named queues with different capacities.

Create multiple named queues with custom capacities.

Enqueue valid drink orders in line (latte, tea, macchiato, Americano, and mocha).

Give precise error messages when rejecting items that are invalid or full queues.

Turn by turn, run the round-robin scheduler.

For each event—create, enqueue, run, work, complete, refuse, and skip—print thorough logs.

Task IDs are automatically generated for each queue (<queue_name>-NNN).
## How to run
 On Windows:
bash
python src/cli.py

Enter commands interactively in the terminal, e.g.:

CREATE Mobile 3
ENQ Mobile latte
RUN 2
SKIP Mobile
To end a session, enter a blank line and press Enter.
## How to run tests locally
Make sure pytest is installed:pip install pytest
Ensure your pytest.ini file is present in the root directory so that src/ is added to PYTHONPATH
window:
pytest -q
or
python -m pytest -q
You should see all tests as passed

## Complexity Notes
Briefly justify:
Queue Design:
Each queue (QueueRR) is implemented using a list with FIFO behavior. Supports O(1) enqueue/dequeue amortized. Round-robin scheduling is used to select queues in order.

Time Complexity:

enqueue, dequeue: O(1) amortized

run: O(#turns + total_minutes_worked)

Space Complexity:

O(N) for storing tasks in all queues

O(#queues) for metadata (counters, skip flags, queue map)

