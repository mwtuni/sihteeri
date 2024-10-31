import sys
import os
from datetime import datetime, timedelta
import openai  # Ensure you have the openai library installed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage import Storage

class AssignmentsAgent:
    description = "Tracks assignment deadlines, statuses, provides reminders, and scores assignments based on answer content."

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

    def score(self, task_name: str) -> str:
        """
        Scores an assignment by comparing the assignment content with the answer content using ChatGPT.
        
        Parameters:
            task_name (str): The name of the task to be scored.
        
        Returns:
            str: The response from ChatGPT with the score or evaluation.
        """
        assignments_folder = "C:/workspace/mwtuni/data/assignments"
        answers_folder = "C:/workspace/mwtuni/data/answers"

        # Construct file paths
        assignment_file_path = os.path.join(assignments_folder, f"{task_name}_2024-09-24")
        answer_file_path = os.path.join(answers_folder, task_name)

        # Check if both files exist
        if not os.path.exists(assignment_file_path):
            return f"Assignment file for '{task_name}' not found."
        if not os.path.exists(answer_file_path):
            return f"Answer file for '{task_name}' not found."

        # Read the contents of the assignment and answer files
        with open(assignment_file_path, 'r', encoding='utf-8') as f:
            assignment_content = f.read()
        with open(answer_file_path, 'r', encoding='utf-8') as f:
            answer_content = f.read()

        # Prepare the ChatGPT messages for completion
        messages = [
            {"role": "system", "content": "You are an assistant evaluating student assignments."},
            {"role": "user", "content": f"Score the following answer based on the given assignment instructions:\n\nAssignment:\n{assignment_content}\n\nAnswer:\n{answer_content}\n\nProvide a score and feedback."}
        ]

        # ChatGPT API Call (self-contained within the function)
        try:
            # Fetch API key and set up the API key for OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return "Error: OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable."

            import openai  # Import here to keep ChatGPT usage encapsulated
            openai.api_key = api_key

            # Send messages to ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            score_response = response['choices'][0]['message']['content']
            return f"Score and Feedback:\n{score_response}"

        except Exception as e:
            return f"Error scoring assignment: {str(e)}"
