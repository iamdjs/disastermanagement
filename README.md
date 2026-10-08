# SurakshaSetu AI — Smart Disaster Management Platform

SurakshaSetu AI is a complete hackathon-ready disaster-management and emergency-coordination platform built with Python, Streamlit, SQLite, Plotly, and optional AI/weather integrations.

## Main Features

### Citizen
- Emergency reporting with severity, casualties, trapped persons, GPS, description, and photo
- Nearest-shelter finder
- Emergency resource requests
- Missing-person registry
- Disaster preparedness guides
- AI/rule-based emergency assistant

### Responder
- Priority-ranked incident queue
- Incident assignment and resolution
- Resource-request prioritization
- Volunteer coordination
- Shelter occupancy management

### Admin
- Emergency Command Dashboard
- Incident and casualty KPIs
- Disaster-type analytics
- Incident map
- Ward risk hotspot scoring
- Shelter occupancy analytics
- Optional live weather monitor
- Optional AI Command Advisor

## Smart Incident Priority

The incident score considers:

- Disaster type
- Severity
- People affected
- Injured persons
- Trapped persons
- Time since the report

The result is normalized to a 0–100 scale.

## Ward Risk Hotspots

The ward-level risk score considers:

- Number of open incidents
- Severe incidents
- Affected population
- Trapped persons
- Average priority score

## Nearest Shelter Search

The project uses the Haversine distance formula to rank shelters by geographic distance. This means the basic project does not require a paid maps API.

## Optional AI

Add a Groq API key inside `.env`:

```env
GROQ_API_KEY=your_key
```

When the key is blank, the project automatically uses its built-in emergency guidance engine.

## Optional Live Weather

Add an OpenWeather key:

```env
OPENWEATHER_API_KEY=your_key
WEATHER_CITY=Guwahati
```

The Weather Monitor can display:

- Temperature
- Humidity
- Wind speed
- Current weather condition

## Installation

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Windows users can also use `run_app.bat`.

## Default Admin Password

```text
admin123
```

Change it in `.env`.

## Project Structure

```text
suraksha_setu_disaster_management/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── HOW_IBM_BOB_WAS_USED.md
├── run_app.bat
├── .streamlit/
│   └── config.toml
├── data/
│   └── suraksha.db
├── uploads/
└── utils/
    ├── database.py
    ├── logic.py
    └── services.py
```

## Problem Statement

Disasters such as floods, fires, earthquakes, landslides, cyclones, storms, and heatwaves can affect communities within minutes. During an emergency, information is often scattered across phone calls, social media, volunteers, local authorities, hospitals, shelters, and rescue teams. This makes it difficult to identify the most urgent incidents and allocate limited rescue resources efficiently.

Citizens may not know where the nearest safe shelter is, how to request food or medical assistance, or where to register a missing family member. Emergency responders need a clear view of casualties, trapped people, resource requirements, shelter conditions, and high-risk locations. Administrators also need a unified command dashboard to monitor the disaster in real time.

Manual coordination may cause delays, duplicated effort, missed reports, poor resource allocation, and overcrowded shelters. A low-cost digital system is needed to connect citizens, responders, volunteers, shelters, and emergency administrators through a single platform.

## Solution Statement

SurakshaSetu AI is a digital disaster-management and emergency-coordination platform built using Python, Streamlit, and SQLite.

Citizens can submit emergency reports containing the disaster type, severity, location, GPS coordinates, affected population, injuries, trapped persons, description, and optional photo evidence. The platform automatically calculates an incident priority score so response teams can focus first on the most critical situations.

Citizens can also request food, drinking water, transport, rescue, medical assistance, and temporary shelter. A nearest-shelter feature ranks available shelters using geographic distance. The system includes a missing-person registry and disaster-specific preparedness guidance.

Responders receive a priority-ranked queue of incidents, can assign teams, resolve incidents, manage resource requests, coordinate volunteers, and update shelter occupancy.

Administrators receive an Emergency Command Dashboard with active incidents, critical incidents, people affected, trapped persons, disaster-type analytics, incident maps, ward-level risk hotspots, and shelter analytics. Optional OpenWeather integration provides live weather information, while optional Groq integration provides AI-supported emergency guidance.

The core system continues to work even without external APIs.

## Hackathon Pitch

"SurakshaSetu AI converts scattered disaster information into one actionable emergency command system. It prioritizes incidents, tracks casualties and trapped people, finds nearby shelters, coordinates resources and volunteers, detects high-risk zones, and provides a live operational picture—all through a low-cost platform designed to keep working even without paid AI services."

## Suggested Demo Flow

1. A citizen reports a flood with trapped people.
2. The system assigns a high priority score.
3. The responder dashboard places the incident near the top.
4. The ward risk score increases.
5. The citizen finds the nearest available shelter.
6. Another citizen requests drinking water and medical help.
7. A responder fulfills the request.
8. A shelter operator updates occupancy.
9. The admin dashboard reflects the updated emergency situation.
10. The AI Command Advisor provides response suggestions.
11. The Weather Monitor can show live conditions when its API key is configured.

## Future Improvements

- SMS and WhatsApp emergency reporting
- Multilingual interface
- GIS flood/landslide layers
- Drone image integration
- Satellite imagery
- Road-aware routing
- Ambulance tracking
- Hospital capacity
- IoT river-level sensors
- Automated public alerts
- Offline-first mobile app
- Damage assessment
- Relief distribution tracking
- Government emergency-service integration
