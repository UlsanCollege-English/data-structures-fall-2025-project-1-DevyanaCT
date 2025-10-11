from dataclasses import dataclass
from typing import Dict, List, Optional

REQUIRED_MENU: Dict[str, int] = {
    "americano": 2,
    "latte": 3,
    "cappuccino": 3,
    "mocha": 4,
    "tea": 1,
    "macchiato": 2,
    "hot_chocolate": 4,
}


@dataclass
class Task:
    task_id: str
    remaining: int


class QueueRR:
    """FIFO queue implemented with a list for tasks."""

    def __init__(self, queue_id: str, capacity: int) -> None:
        self.queue_id = queue_id
        self.capacity = capacity
        self._tasks: List[Task] = []

    def enqueue(self, task: Task) -> bool:
        if len(self._tasks) >= self.capacity:
            return False
        self._tasks.append(task)
        return True

    def dequeue(self) -> Optional[Task]:
        if not self._tasks:
            return None
        return self._tasks.pop(0)

    def peek(self) -> Optional[Task]:
        if not self._tasks:
            return None
        return self._tasks[0]

    def __len__(self) -> int:
        return len(self._tasks)

    def all_tasks(self) -> List[Task]:
        return self._tasks[:]


class Scheduler:
    def __init__(self) -> None:
        self.time = 0
        self.queues: List[QueueRR] = []
        self.queue_map: Dict[str, QueueRR] = {}
        self.id_counters: Dict[str, int] = {}
        self.skip_flags: Dict[str, bool] = {}
        self.rr_index = 0
        self.menu_items = REQUIRED_MENU.copy()

    # ----- Helpers -----
    def menu(self) -> Dict[str, int]:
        return self.menu_items.copy()

    def next_queue(self) -> Optional[str]:
        if not self.queues:
            return None
        return self.queues[self.rr_index].queue_id

    # ----- Commands -----
    def create_queue(self, queue_id: str, capacity: int) -> List[str]:
        if queue_id in self.queue_map:
            return [f"time={self.time} event=error reason=queue_exists"]
        q = QueueRR(queue_id, capacity)
        self.queues.append(q)
        self.queue_map[queue_id] = q
        self.id_counters[queue_id] = 0
        self.skip_flags[queue_id] = False
        return [f"time={self.time} event=create queue={queue_id}"]

    def enqueue(self, queue_id: str, item_name: str) -> List[str]:
        logs: List[str] = []
        if item_name not in self.menu_items:
            print("Sorry, we don't serve that.")
            logs.append(f"time={self.time} event=reject queue={queue_id} reason=unknown_item")
            return logs

        if queue_id not in self.queue_map:
            logs.append(f"time={self.time} event=error reason=queue_not_found")
            return logs

        # Generate task_id
        self.id_counters[queue_id] += 1
        task_id = f"{queue_id}-{self.id_counters[queue_id]:03d}"
        task = Task(task_id, self.menu_items[item_name])

        success = self.queue_map[queue_id].enqueue(task)
        if success:
            logs.append(f"time={self.time} event=enqueue queue={queue_id} task={task_id} remaining={task.remaining}")
        else:
            print("Sorry, we're at capacity.")
            logs.append(f"time={self.time} event=reject queue={queue_id} reason=full")
        return logs

    def mark_skip(self, queue_id: str) -> List[str]:
        if queue_id in self.skip_flags:
            self.skip_flags[queue_id] = True
            return [f"time={self.time} event=skip queue={queue_id}"]
        else:
            return [f"time={self.time} event=error reason=queue_not_found"]

    def run(self, quantum: int, steps: Optional[int]) -> List[str]:
        logs: List[str] = []

        if steps is None:
            steps = len(self.queues)

        if steps < 1 or steps > len(self.queues):
            logs.append(f"time={self.time} event=error reason=invalid_steps")
            return logs

        visited = 0
        while visited < steps:
            if not self.queues:
                break

            q = self.queues[self.rr_index]
            qid = q.queue_id
            logs.append(f"time={self.time} event=run queue={qid}")

            if self.skip_flags[qid]:
                self.skip_flags[qid] = False
            else:
                task = q.peek()
                if task:
                    work_time = min(task.remaining, quantum)
                    task.remaining -= work_time
                    self.time += work_time
                    logs.append(f"time={self.time} event=work queue={qid} task={task.task_id} done={work_time}")
                    if task.remaining == 0:
                        q.dequeue()
                        logs.append(f"time={self.time} event=finish queue={qid} task={task.task_id}")

            # Move to next queue RR
            self.rr_index = (self.rr_index + 1) % len(self.queues)
            visited += 1

        return logs

    # ----- Display -----
    def display(self) -> List[str]:
        lines: List[str] = []
        lines.append(f"display time={self.time} next={self.next_queue()}")
        menu_str = ",".join(f"{k}:{v}" for k, v in sorted(self.menu_items.items()))
        lines.append(f"display menu=[{menu_str}]")
        for q in self.queues:
            tasks = ",".join(f"{t.task_id}:{t.remaining}" for t in q.all_tasks())
            skip_str = " skip" if self.skip_flags[q.queue_id] else ""
            lines.append(f"display {q.queue_id} [{len(q)}/{q.capacity}]{skip_str} -> [{tasks}]")
        return lines