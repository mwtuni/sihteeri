from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from manager import Manager 
from chatgpt import interpret_prompt  # Tuodaan interpret_prompt chatgpt.py:stä
import json

app = Flask(__name__)

manager = Manager()

# System-prompt definition: instructs ChatGPT API to interpret user prompt
def generate_system_prompt():
    agents_list = "\n".join([f"{i+1}. {agent['name']} - {agent['description']}" for i, agent in enumerate(manager.get_agents_list())])
    system_prompt = f"""
Olet Sihteerin avustaja, joka osaa käyttää seuraavia agentteja:
{agents_list}

Tehtäväsi on ottaa käyttäjän prompt, päättää mitä toimintoja (agentteja) käytetään, antaa agenteille englanninkieliset ohjeet ja palauttaa tehtävälista JSON-muodossa.
Esimerkki: Jos prompt olisi: "Milloin seuraava kurssi alkaa? Olenko palauttanut kotitehtäväni?",
niin JSON-tehtävälistan rakenne tulisi näyttää tältä:
{{
  "tasks": [
    {{
      "agent": "calendar_agent",
      "instructions": "Return the next course lesson information"
    }},
    {{
      "agent": "moodle_agent",
      "instructions": "Check if user has returned homework"
    }}
  ]
}}
Palauta vain ne tehtävät, jotka ovat relevantteja käyttäjän promptin perusteella.
"""
    return system_prompt.strip()

SYSTEM_PROMPT = generate_system_prompt()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip()
    sender_number = request.form.get('From')

    response_text = ""

    if incoming_msg == "list_agents":
        agents_list = manager.get_agents_list()
        response_text = "Käytettävissä olevat agentit:\n" + "\n".join([f"{agent['name']} - {agent['description']}" for agent in agents_list])
        response = MessagingResponse()
        response.message(response_text)
        return str(response)

    elif incoming_msg == "system_prompt":
        return SYSTEM_PROMPT, 200

    else:
        print("Processing user prompt:", incoming_msg)
        try:
            # Interpret user prompt with ChatGPT API
            task_list = json.loads(interpret_prompt(incoming_msg, SYSTEM_PROMPT))
            print("Task list:", task_list)
            
            # Käydään läpi tehtävät JSON-tehtävälistasta ja suoritetaan agentin kutsu
            for task in task_list.get("tasks", []):
                agent_name = task["agent"]
                instructions = task["instructions"]
                
                # Hakee agentin nimen perusteella
                print("Looking for agent by name: ", agent_name)
                agent = manager.get_agent_by_name(agent_name)
                
                if agent:

                    if agent_name == "timetable_agent":
                        print("Getting next class info")
                        response_text = agent.get_next_class()  # timetable_agent hakee seuraavan luennon
                        print("Response from agent:", response_text)
                        break
                else:
                    response_text = f"Agent {agent_name} ei ole tuettu."

        except Exception as e:
            response_text = f"Error processing your prompt: {str(e)}"

        # Twilio response        
        response = MessagingResponse()
        response.message(response_text)  # Vain agentin palauttama teksti palautetaan käyttäjälle
        return str(response)


def print_public_ip():
    try:
        public_ip = requests.get("https://api.ipify.org").text
        print(f"Sihteeri on käytettävissä julkisella IP-osoitteella: {public_ip}")
    except requests.RequestException as e:
        print(f"Julkisen IP-osoitteen hakeminen epäonnistui: {e}")

if __name__ == "__main__":
    print_public_ip() 
    app.run(host="0.0.0.0", port=5000)
