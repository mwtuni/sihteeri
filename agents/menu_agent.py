# agents/menu_agent.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from ollama_rag import OllamaRAG

class MenuAgent:
    description = "Finds out today's lunch menu."

    def __init__(self):
        """
        Initializes the MenuAgent for retrieving today's lunch menu.
        """
        self.rag = OllamaRAG()
        self.rag.setup_vectorstore(["http://127.0.0.1:8088/menub.txt"])

    def get_today_menu(self):
        """
        Retrieves today's lunch menu by querying the LLM + RAG.
        """
        today = datetime.now().strftime("%d.%m.%Y")
        prompt = f"What is for lunch on {today}?"
        return self.rag.query(prompt)

# Example usage
if __name__ == "__main__":
    agent = MenuAgent()
    print(agent.get_today_menu())
