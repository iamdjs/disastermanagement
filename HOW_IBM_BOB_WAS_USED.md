# How IBM Bob Was Used in SurakshaSetu AI

## Overview

IBM Bob was used as an AI coding assistant during the development of SurakshaSetu AI. It supported requirement analysis, architecture planning, multi-file code generation, debugging, refactoring, configuration, validation, and documentation.

The developer remained responsible for feature selection, reviewing generated code, validating safety logic, testing the project, and preparing the final hackathon demonstration.

## 1. Ask Mode

IBM Bob was used to explore the disaster-management problem before implementation.

Example questions:

- What information should an emergency report contain?
- How should emergency incidents be prioritized?
- How can citizens find shelters without a paid maps API?
- What information should a shelter-management module track?
- How can resource requests be prioritized?
- How can a ward-level disaster risk score be calculated?
- Which features should still work without internet access?
- How should AI and weather API keys be stored?

Ask Mode helped identify the following modules:

- Emergency reporting
- Smart incident prioritization
- Emergency resource requests
- Shelter management
- Nearest-shelter search
- Missing-person registry
- Volunteer coordination
- Response-team assignment
- Ward risk analytics
- Weather monitoring
- AI emergency assistance
- Preparedness guidance

## 2. Plan Mode

IBM Bob was then used to create a modular development plan.

The project was separated into:

```text
app.py
utils/database.py
utils/logic.py
utils/services.py
.env
.env.example
README.md
HOW_IBM_BOB_WAS_USED.md
```

### `app.py`

Bob helped organize the Streamlit interface into separate roles:

- Citizen
- Responder
- Admin

### `utils/database.py`

IBM Bob assisted in defining SQLite tables for:

- Incidents
- Shelters
- Emergency resource requests
- Volunteers
- Response tasks
- Missing people

### `utils/logic.py`

Bob helped isolate reusable logic for:

- Incident priority scoring
- Ward risk scoring
- Shelter occupancy calculation
- Resource-request priority
- Haversine distance
- Nearest-shelter ranking
- Disaster preparedness guidance

### `utils/services.py`

Bob helped structure:

- Groq API integration
- Rule-based AI fallback
- OpenWeather integration
- Network/API error handling

## 3. Agent Mode

IBM Bob was used in Agent Mode to help generate and modify code across the project.

It assisted with:

- Building the SQLite schema
- Adding demo emergency data
- Creating Streamlit forms
- Adding file/photo uploads
- Building incident scoring
- Creating responder queues
- Implementing team assignment
- Adding resource workflows
- Building shelter-management tools
- Implementing volunteer registration
- Creating the missing-person registry
- Adding risk dashboards
- Adding maps and charts
- Connecting `.env` variables
- Integrating Groq
- Integrating OpenWeather
- Adding fallback logic
- Improving validation and error handling

## 4. Incident Priority Algorithm

IBM Bob helped transform multiple emergency factors into one transparent score.

The score considers:

- Disaster type
- Severity
- Number of people affected
- Injuries
- Trapped persons
- Time since the incident was reported

Higher-risk disaster types such as earthquakes, fires, landslides, and floods receive additional weighting.

The final score is limited to 100.

## 5. Ward Risk Hotspot Logic

IBM Bob helped design the ward-level risk model.

It uses:

- Open incident count
- Severe incident count
- Total people affected
- Number of trapped people
- Average incident priority

This allows the command dashboard to identify locations requiring urgent attention.

## 6. Shelter Intelligence

IBM Bob assisted in creating shelter logic based on:

- Maximum capacity
- Current occupancy
- Food stock
- Water stock
- Medical kits
- GPS coordinates
- Operational status

Occupancy is classified as:

- AVAILABLE
- BUSY
- NEAR FULL
- FULL

## 7. Nearest Shelter Calculation

IBM Bob helped implement the Haversine formula to calculate approximate geographic distance between a citizen and each shelter.

This avoids requiring a paid routing API for the core prototype.

## 8. Environment Configuration

IBM Bob helped move configuration and API keys into `.env`.

The project uses:

```env
APP_NAME
REGION_NAME
ADMIN_PASSWORD
GROQ_API_KEY
GROQ_MODEL
OPENWEATHER_API_KEY
WEATHER_CITY
EOC_LAT
EOC_LON
HIGH_RISK_THRESHOLD
CRITICAL_INCIDENT_THRESHOLD
MAX_SHELTER_OCCUPANCY_ALERT
```

This keeps configuration separate from source code.

## 9. AI Assistant

IBM Bob helped design the AI layer so that the application remains functional without an external AI provider.

Flow:

```text
User Question
      |
      v
Is GROQ_API_KEY available?
     / \
   Yes  No
   |     |
 Groq   Built-in emergency guidance
   |     |
   +----> Response
```

If a Groq request fails, the project automatically falls back to built-in emergency guidance.

## 10. Weather Integration

IBM Bob assisted with optional OpenWeather integration.

When a key is available, the application can display:

- Current temperature
- Humidity
- Wind speed
- Weather conditions

When the key is missing, the application continues operating normally.

## 11. Validation and Error Handling

IBM Bob was used to review common failure cases such as:

- Empty database results
- Missing GPS coordinates
- Missing upload directories
- Invalid API keys
- Network failures
- Full shelters
- Invalid form entries
- Duplicate Streamlit widget IDs
- Optional services being unavailable

The project uses fallback behavior so that external-service failures do not break the core disaster-management system.

## 12. Refactoring

IBM Bob helped separate database, business logic, and external-service logic from the main UI file.

This improved:

- Readability
- Maintainability
- Reusability
- Debugging
- Hackathon presentation quality

## 13. Documentation

IBM Bob was also used to support:

- README preparation
- Problem statement
- Solution statement
- Installation steps
- `.env` instructions
- Demo flow
- Future enhancements
- IBM Bob usage documentation

## 14. Example IBM Bob Prompts

### Ask Mode

```text
Analyze a disaster-management problem for a hackathon. Identify important
features for citizens, responders, volunteers, shelters, and an emergency
command center. The solution should remain useful even without paid APIs.
```

### Plan Mode

```text
Create an implementation plan for a Streamlit + SQLite disaster-management
system with emergency reporting, priority scoring, emergency resources,
shelters, nearest-shelter search, missing persons, volunteers, responder
tasks, ward risk analytics, .env configuration, optional weather data,
and a Groq-based AI assistant with rule-based fallback.
```

### Agent Mode

```text
Implement the planned project across multiple Python files. Create the
database schema, Streamlit UI, priority logic, shelter calculations,
Haversine distance logic, risk dashboard, resource workflow, volunteer
module, missing-person registry, AI fallback, weather integration,
environment configuration, validation, and project documentation.
```

## Final Summary

IBM Bob helped accelerate SurakshaSetu AI from a disaster-management concept into a working multi-module prototype. Its strongest contributions were architecture planning, multi-file coding, priority and risk logic, database integration, API configuration, fallback handling, refactoring, debugging, and documentation.
