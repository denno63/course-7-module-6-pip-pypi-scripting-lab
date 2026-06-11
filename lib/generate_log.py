import argparse
import os
from datetime import datetime

import requests

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    rich_enabled = True
except ImportError:
    console = None
    rich_enabled = False


class TaskManager:
    def __init__(self, filename="tasks.txt"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        self.tasks = []
        if not os.path.exists(self.filename):
            return
        with open(self.filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip("\n")
                if not line:
                    continue
                complete = line.startswith("[x]")
                description = line[4:].strip() if len(line) > 4 else ""
                self.tasks.append({"description": description, "complete": complete})

    def save_tasks(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            for task in self.tasks:
                status = "x" if task["complete"] else " "
                file.write(f"[{status}] {task['description']}\n")

    def add_task(self, description):
        if not description or not isinstance(description, str):
            raise ValueError("Task description must be a non-empty string.")
        self.tasks.append({"description": description, "complete": False})
        self.save_tasks()
        return len(self.tasks)

    def complete_task(self, task_index):
        if not isinstance(task_index, int) or task_index < 1 or task_index > len(self.tasks):
            raise IndexError("Task index is out of range.")
        self.tasks[task_index - 1]["complete"] = True
        self.save_tasks()

    def list_tasks(self):
        self.load_tasks()
        return self.tasks


def print_message(message):
    if rich_enabled and console is not None:
        console.print(message)
    else:
        print(message)


def fetch_data():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def build_log_entries_from_api(limit=5):
    posts = fetch_data()
    entries = [f"Post {post['id']}: {post['title']}" for post in posts[:limit]]
    return entries


def generate_log(data):
    if not isinstance(data, list):
        raise ValueError("Input data must be a list of log entries.")

    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for entry in data:
            file.write(f"{entry}\n")

    print_message(f"Log written to {filename}")
    return filename


def display_tasks(task_manager):
    tasks = task_manager.list_tasks()
    if not tasks:
        print_message("No tasks found.")
        return

    if rich_enabled and console is not None:
        table = Table(title="Task List")
        table.add_column("#", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Description", justify="left")

        for index, task in enumerate(tasks, start=1):
            status = "✅" if task["complete"] else "🟩"
            table.add_row(str(index), status, task["description"])

        console.print(table)
    else:
        for index, task in enumerate(tasks, start=1):
            status = "[x]" if task["complete"] else "[ ]"
            print(f"{index}. {status} {task['description']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Automation tool for logs and tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("generate-log", help="Generate a dated log file.")
    log_parser.add_argument(
        "--source",
        choices=["default", "api"],
        default="default",
        help="Choose default sample data or fetch data from an API.",
    )

    task_parser = subparsers.add_parser("add-task", help="Add a new task to the task list.")
    task_parser.add_argument("description", help="Description of the task to add.")

    complete_parser = subparsers.add_parser("complete-task", help="Mark an existing task as complete.")
    complete_parser.add_argument("index", type=int, help="1-based index of the task to mark complete.")

    list_parser = subparsers.add_parser("list-tasks", help="List all current tasks.")

    args = parser.parse_args(argv)

    if args.command == "generate-log":
        if args.source == "api":
            entries = build_log_entries_from_api()
        else:
            entries = [
                "User logged in",
                "User updated profile",
                "Report exported",
            ]
        generate_log(entries)

    elif args.command == "add-task":
        manager = TaskManager()
        task_number = manager.add_task(args.description)
        print_message(f"Added task {task_number}: {args.description}")

    elif args.command == "complete-task":
        manager = TaskManager()
        manager.complete_task(args.index)
        print_message(f"Marked task {args.index} as complete.")

    elif args.command == "list-tasks":
        manager = TaskManager()
        display_tasks(manager)


if __name__ == "__main__":
    main()
