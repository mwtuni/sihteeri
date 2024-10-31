import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import Storage
from chatgpt import interpret_prompt

class AssignmentsAgent:
    description = "Tracks assignment deadlines, statuses, and provides reminders."

    def __init__(self):
        self.storage = Storage()
        self._initialize_table()
        self._populate_assignments_from_files()

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

    def _populate_assignments_from_files(self):
        assignments_folder = "C:/workspace/mwtuni/data/assignments"
        answers_folder = "C:/workspace/mwtuni/data/answers"

        # Get lists of assignments and answers
        assignments_files = os.listdir(assignments_folder)
        answers_files = os.listdir(answers_folder)

        for filename in assignments_files:
            if '_' in filename:
                title, due_date_str = filename.rsplit('_', 1)

                try:
                    # Parse date
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
                except ValueError:
                    print(f"Skipping file {filename} due to invalid date format.")
                    continue

                # Determine current status based on presence in answers
                new_status = "submitted" if title in answers_files else "pending"

                # Check if assignment is already in the database
                existing_assignment = self.storage.execute_query(
                    "SELECT id, status FROM assignments WHERE title = ? AND due_date = ?", 
                    (title, due_date)
                )
                
                if existing_assignment:
                    # If the assignment exists and the status has changed, update it
                    assignment_id, current_status = existing_assignment[0]
                    if current_status != new_status:
                        self.storage.update_data("assignments", {"status": new_status}, "id = ?", (assignment_id,))
                        print(f"Updated assignment '{title}' status to '{new_status}' based on answer file presence.")
                else:
                    # Insert new assignment if it does not exist
                    data = {"title": title, "due_date": due_date, "status": new_status}
                    result = self.storage.insert_data("assignments", data, unique_columns=["title", "due_date"])
                    print(f"Inserted: {data if isinstance(result, int) else result}")

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
    
    def score(self, task_name: str) -> str:
        """
        Scores an assignment by comparing the assignment content with the answer content using interpret_prompt from chatgpt.py.

        Parameters:
            task_name (str): The name of the task to be scored.

        Returns:
            str: The score and feedback generated by ChatGPT.
        """
        assignments_folder = "C:/workspace/mwtuni/data/assignments"
        answers_folder = "C:/workspace/mwtuni/data/answers"

        # Construct file paths for assignment and answer
        assignment_files = [f for f in os.listdir(assignments_folder) if f.startswith(task_name)]
        if not assignment_files:
            return f"Assignment file for '{task_name}' not found."
        assignment_file_path = os.path.join(assignments_folder, assignment_files[0])
        answer_file_path = os.path.join(answers_folder, task_name)

        # Check for file existence
        if not os.path.exists(assignment_file_path):
            return f"Assignment file for '{task_name}' not found."
        if not os.path.exists(answer_file_path):
            return f"Answer file for '{task_name}' not found."

        # Read contents of the assignment and answer files
        with open(assignment_file_path, 'r', encoding='utf-8') as f:
            assignment_content = f.read()
        with open(answer_file_path, 'r', encoding='utf-8') as f:
            answer_content = f.read()
        print("Assignment content:", assignment_content)
        print("Answer content:", answer_content)

        # Define the system prompt with evaluation instructions in Finnish
        system_prompt = (
            "Olet opetusavustaja, jonka tehtävänä on arvioida opiskelijoiden tehtäviä. "
            "Tehtäväsi on lukea tehtävän ohjeet ja opiskelijan vastaus, ja antaa sen jälkeen arvosana ja palautetta. "
            "Anna rakentavaa palautetta mainiten vahvuudet ja kehityskohteet."
        )

        # Combine assignment and answer into a single user prompt in Finnish
        user_prompt = (
            f"Arvioi opiskelijan vastaus annetun tehtävän ohjeiden perusteella.\n\n"
            f"Tehtävä:\n{assignment_content}\n\nVastaus:\n{answer_content}\n\n"
            "Anna arvosana asteikolla 1–5 ja yksityiskohtainen palaute. Anna lopuksi esimerkki täydellisestä vastauksesta."
        )

        # Call interpret_prompt from chatgpt.py and return the result
        return interpret_prompt(user_prompt, system_prompt)    

# Example usage
if __name__ == "__main__":
    agent = AssignmentsAgent()
    print(agent.get_upcoming_assignments(7))
    print(agent.get_due_soon(2))
