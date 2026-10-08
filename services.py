import os
import requests
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """
You are SurakshaSetu AI, a disaster-management assistant.
Give concise, safety-first guidance. Do not claim to replace emergency services.
For immediate danger, advise contacting local emergency authorities and moving to safety.
"""

def rule_based_emergency_answer(question):
    q = question.lower()
    if "flood" in q:
        return "Move to higher ground, avoid floodwater, keep medicines and documents protected, and follow official evacuation alerts."
    if "fire" in q:
        return "Raise the alarm, evacuate immediately using the safest exit, stay low in smoke, call emergency services, and do not re-enter."
    if "earthquake" in q:
        return "Drop, cover and hold on during shaking. After it stops, move carefully to a safe open area and expect aftershocks."
    if "landslide" in q:
        return "Move away from slopes and drainage channels, avoid unstable debris, and evacuate early if warning signs appear."
    if "cyclone" in q or "storm" in q:
        return "Stay indoors away from windows, secure loose objects before conditions worsen, charge devices, and follow official evacuation instructions."
    if "heat" in q:
        return "Drink water regularly, avoid peak-hour outdoor work, use shade, check vulnerable people, and seek urgent help for suspected heat stroke."
    return "If there is immediate danger, contact local emergency services and move to a safer location. Share the exact location, disaster type, casualties, trapped persons and urgent needs."

def ask_ai(question, context=""):
    key=os.getenv("GROQ_API_KEY","").strip()
    model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant").strip()
    if not key:
        return rule_based_emergency_answer(question), "Rule-based emergency mode"
    try:
        r=requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={
                "model":model,
                "messages":[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":f"Operational context:\n{context}\n\nQuestion:\n{question}"}
                ],
                "temperature":0.2,
                "max_tokens":500
            },
            timeout=25
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"], f"AI mode: {model}"
    except Exception:
        return rule_based_emergency_answer(question), "Fallback emergency mode"

def get_weather():
    api_key=os.getenv("OPENWEATHER_API_KEY","").strip()
    city=os.getenv("WEATHER_CITY","Guwahati").strip()
    if not api_key:
        return {"available":False,"city":city,"message":"Add OPENWEATHER_API_KEY to .env for live weather."}
    try:
        r=requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q":city,"appid":api_key,"units":"metric"},
            timeout=20
        )
        r.raise_for_status()
        d=r.json()
        return {
            "available":True,"city":city,"temperature":d["main"]["temp"],
            "humidity":d["main"]["humidity"],"wind_speed":d["wind"]["speed"],
            "condition":d["weather"][0]["description"].title()
        }
    except Exception:
        return {"available":False,"city":city,"message":"Weather service is currently unavailable."}
