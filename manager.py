import os
import importlib
import inspect

class Manager:
    def __init__(self):
        # Dictionary to hold dynamically loaded agents by filename
        self.agents = {}
        
        # Dynamically load agents from the agents folder
        self.load_agents()

    def load_agents(self):
        """
        Dynamically loads all agents in the agents folder using the filename as the key,
        and populates the agents dictionary with the agent instances and their descriptions.
        """
        agents_path = os.path.join(os.path.dirname(__file__), 'agents')
        for filename in os.listdir(agents_path):
            # Process only Python files, ignore __init__.py
            if filename.endswith('.py') and filename != '__init__.py':
                agent_name = filename[:-3]  # Remove the '.py' extension
                module_name = f'agents.{agent_name}'
                module = importlib.import_module(module_name)

                # Find the first class in the module to use as the agent
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    # Ensure the class is defined in the current module
                    if obj.__module__ == module_name:
                        # Instantiate the agent and retrieve its description
                        agent_instance = obj()
                        description = getattr(agent_instance, "description", "No description provided")
                        
                        # Store the agent instance and description with the filename as the key
                        self.agents[agent_name] = {
                            "instance": agent_instance,
                            "description": description
                        }
                        break  # Stop after the first class is found

    def get_agents_list(self):
        """
        Returns a list of all loaded agents with their descriptions.
        """
        return [{"name": name, "description": data["description"]} for name, data in self.agents.items()]

    def get_agent_by_name(self, name):
        """
        Retrieves an agent instance by filename-based name if it exists in the loaded agents.
        """
        return self.agents.get(name, {}).get("instance")
