# Sihteeri - Personal AI assistant with private back-end

Sihteeri is an AI assistant designed for university students with a strong emphasis on data privacy. The system operates on a private server backend, running local AI models to ensure the confidentiality of sensitive data. It integrates both front-end and back-end components to facilitate secure interactions via multiple channels.

## Architecture Overview

![image](https://github.com/user-attachments/assets/cd4bda5e-2d6a-468f-ad5c-f0235391e931)

### Front-End Components
The front-end consists of multiple interfaces that users can interact with:

- **WhatsApp**: Communication with the AI via WhatsApp is enabled using Twilio's integration. This allows users to send and receive messages through their WhatsApp accounts.
- **Gradio**: Provides a web-based user interface for interaction, allowing users to interact with the AI via web browsers. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mwtuni/sihteeri/blob/main/gradio.ipynb)
- **Google Colaboratory (Colab)**: Offers a cloud-based Jupyter notebook environment for users, making it possible to run AI models and scripts in an interactive way. 

These front-end channels are facilitated by Twilio, which acts as a bridge to ensure communication between the front-end and back-end services.

### Back-End Components
The back-end handles processing requests, managing data, and serving the AI functionality:

- **Python**: Serves as the core programming language for building the back-end logic. It integrates with various libraries and frameworks to power the AI functionalities.
- **Flask**: A lightweight WSGI web framework used to develop RESTful APIs that handle communication between front-end and back-end components.
- **ChatGPT API**: Used exclusively for interpreting user prompts. **It does not have access to any private or confidential data**; all sensitive data processing is handled by local models.
- **Ollama**: A platform for running large language models locally, ensuring that private data remains within the server. It provides an alternative to using external AI services.
- **SQLite**: Used for database management, likely storing user interactions, session data, or other necessary information required for processing.

### Data Flow and Communication

- **Twilio**: Acts as a communication intermediary, receiving messages from WhatsApp and sending them to the Flask server. It also relays responses back to the user’s WhatsApp.
- **Flask Server**: The Flask server processes incoming requests, interfaces with Python code, and accesses either the ChatGPT API, Ollama, or the SQLite database as needed to generate responses.
- **AI Model Integration**: Depending on the nature of the request, the system routes prompts to the ChatGPT API for interpretation but handles all private data with local models via Ollama.
- **Gradio and Colab Interfaces**: Communicate directly with the Flask backend, enabling users to interact with the AI through their browsers or Colab notebooks.

### Security and Privacy Considerations

- The ChatGPT API is strictly used for understanding the user prompt and has no access to any private data.
- Sensitive and confidential data is processed using local models running on Ollama and stored securely in SQLite.
- By using Flask and Python on a private server, the architecture ensures that all data remains within a controlled environment, enhancing privacy.

## Technologies Summary

| **Component**   | **Role**                                  | **Technology**         |
|-----------------|------------------------------------------|------------------------|
| WhatsApp        | User Interaction Interface               | Twilio Integration     |
| Gradio          | Web Interface                            | Gradio Library         |
| Google Colab    | Cloud-Based Interactive Environment      | Colaboratory Notebook  |
| Python          | Core Backend Logic                       | Python Programming     |
| Flask           | Web Framework for API & Backend Logic    | Flask                  |
| ChatGPT API     | External AI Model Access (Prompt Only)   | OpenAI’s API           |
| Ollama          | Local AI Model Execution                 | Ollama                 |
| SQLite          | Database Management                      | SQLite Database        |
| Twilio          | Communication Gateway                    | Twilio API             |

### Data Flow Summary
- Users interact with the system via WhatsApp, Gradio, or Colab.
- Messages from WhatsApp are routed through Twilio to the Flask server.
- The Flask server processes the request using Python logic, which may involve interpreting prompts through the ChatGPT API but handles all private data using local AI models (Ollama) or SQLite.
- The response is generated and sent back through the respective front-end channel, ensuring a secure and smooth user experience.

This architecture provides a flexible, privacy-focused AI assistant that can operate within a controlled, secure environment, making it well-suited for university students handling sensitive data.

