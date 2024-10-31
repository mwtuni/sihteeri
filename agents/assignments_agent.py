import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import Storage

class AssignmentsAgent:
    description = "Tracks assignment deadlines, statuses, and provides reminders."

    def __init__(self):
        self.storage = Storage()
        self._initialize_table()

    def _initialize_table(self):
        schema = {
            "table": "assignments",
            "fields": {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "title": "TEXT NOT NULL",
                "due_date": "TEXT NOT NULL",
                "status": "TEXT NOT NULL DEFAULT 'pending'"
            },
            "constraints": ["UNIQUE(title, due_date)"]
        }
        self.storage.create_table(schema)

    def add_assignment(self, title, due_date):
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            data = {"title": title, "due_date": due_date, "status": "pending"}
            result = self.storage.insert_data("assignments", data, unique_columns=["title", "due_date"])
            return result if isinstance(result, str) else f"Assignment '{title}' added with ID {result}."
        except ValueError:
            return "Error: Invalid date format. Please use 'YYYY-MM-DD'."

    def get_upcoming_assignments(self, days_ahead=7):
        now = datetime.now()
        upcoming_date = now + timedelta(days=days_ahead)
        rows = self.storage.fetch_rows_by_date_range("assignments", "due_date", now, upcoming_date, status="pending")
        
        if not rows:
            return f"No assignments due in the next {days_ahead} days."
        
        result = "Upcoming assignments:\n"
        for row in rows:
            result += f"- {row['title']} (Due: {row['due_date']})\n"
        return result

    def mark_assignment_completed(self, assignment_id):
        success = self.storage.update_data("assignments", {"status": "completed"}, "id = ?", (assignment_id,))
        return f"Assignment with ID {assignment_id} marked as completed." if success else f"Assignment with ID {assignment_id} not found."

    def get_due_soon(self, days_ahead=2):
        now = datetime.now()
        due_soon_date = now + timedelta(days=days_ahead)
        rows = self.storage.fetch_rows_by_date_range("assignments", "due_date", now, due_soon_date, status="pending")
        
        if not rows:
            return "No assignments are due soon."
        
        result = "Assignments due soon:\n"
        for row in rows:
            result += f"- {row['title']} (Due: {row['due_date']})\n"
        return result

# Example usage
if __name__ == "__main__":
    agent = AssignmentsAgent()
    print(agent.add_assignment("Math Homework", "2024-11-01"))
    print(agent.add_assignment("Physics Project", "2024-11-05"))
    print(agent.get_upcoming_assignments(7))
    print(agent.mark_assignment_completed(1))
    print(agent.get_due_soon(2))
