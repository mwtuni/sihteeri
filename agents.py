class Agents:
    def __init__(self):
        self.agents = [
            {"name": "vlm_agent", "description": "vision language model kuvien tulkitsemiseen"},
            {"name": "llm_agent", "description": "luonnollisen kielen käsittely"},
            {"name": "rvc_agent", "description": "äänen muokkaus ja muunnos"},
            {"name": "sd_agent", "description": "stable diffusion kuvien generointi"},
            {"name": "http_agent", "description": "HTTP-pyyntöjen käsittely"},
            {"name": "sms_agent", "description": "SMS-viestien lähetys"},
            {"name": "weather_agent", "description": "säätietojen hakeminen"},
            {"name": "moodle_agent", "description": "Moodlen kurssimateriaalien hallinta"},
            {"name": "calendar_agent", "description": "kalenteritapahtumien hallinta"}
        ]

    def get_agents_list(self):
        return self.agents
