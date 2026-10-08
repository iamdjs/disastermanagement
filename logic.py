from datetime import datetime
import math

DISASTER_BONUS = {
    "Earthquake":24,"Fire":22,"Landslide":20,"Flood":18,
    "Cyclone":18,"Storm":12,"Heatwave":10,"Other":8
}

def incident_priority(disaster_type, severity, people_affected, injured, trapped, created_at):
    try:
        created = datetime.fromisoformat(created_at)
    except Exception:
        created = datetime.now()
    age_hours = max(0, (datetime.now()-created).total_seconds()/3600)
    score = (
        severity*9 + min(people_affected,500)*0.08 + min(injured,100)*2.8
        + min(trapped,50)*5 + min(age_hours,48)*0.45
        + DISASTER_BONUS.get(disaster_type,8)
    )
    return round(min(score,100),1)

def ward_risk_score(open_incidents, severe_incidents, affected_people, trapped_people, avg_priority):
    score = (
        open_incidents*7 + severe_incidents*12 + min(affected_people,1000)*0.035
        + min(trapped_people,100)*0.8 + avg_priority*0.35
    )
    return round(min(score,100),1)

def shelter_occupancy_percent(occupied, capacity):
    return round((occupied/capacity)*100,1) if capacity else 0

def shelter_status(occupied, capacity, alert_threshold=90):
    pct = shelter_occupancy_percent(occupied, capacity)
    if pct >= 100: return "FULL"
    if pct >= alert_threshold: return "NEAR FULL"
    if pct >= 70: return "BUSY"
    return "AVAILABLE"

def resource_priority(urgency, quantity, created_at):
    try:
        created = datetime.fromisoformat(created_at)
    except Exception:
        created = datetime.now()
    hours = max(0,(datetime.now()-created).total_seconds()/3600)
    return round(min(100, urgency*15 + min(quantity,500)*0.1 + min(hours,48)*0.5),1)

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1,p2 = math.radians(lat1),math.radians(lat2)
    dp,dl = math.radians(lat2-lat1),math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))

def nearest_shelters(lat, lon, shelters):
    ranked=[]
    for shelter in shelters:
        s=dict(shelter)
        if s.get("lat") is None or s.get("lon") is None:
            continue
        s["distance_km"]=round(haversine_km(lat,lon,float(s["lat"]),float(s["lon"])),2)
        ranked.append(s)
    return sorted(ranked,key=lambda x:x["distance_km"])

PREPAREDNESS = {
    "Flood":[
        "Move important documents and medicines to waterproof bags.",
        "Keep drinking water, dry food, torch and power bank ready.",
        "Avoid walking or driving through fast-moving floodwater.",
        "Switch off electricity if water enters the house and it is safe to do so.",
        "Move to higher ground when instructed."
    ],
    "Earthquake":[
        "Drop, cover and hold on during shaking.",
        "Stay away from glass and tall furniture.",
        "After shaking stops, move carefully to an open safe area.",
        "Do not use lifts.",
        "Expect aftershocks."
    ],
    "Fire":[
        "Raise the alarm and call emergency services.",
        "Evacuate using the safest route.",
        "Stay low if there is smoke.",
        "Do not re-enter a burning building.",
        "Use an extinguisher only if trained and your escape route is clear."
    ],
    "Cyclone":[
        "Stay indoors away from windows.",
        "Secure loose outdoor objects before conditions worsen.",
        "Charge phones and power banks.",
        "Keep emergency food, water and medicine ready.",
        "Follow official evacuation instructions."
    ],
    "Landslide":[
        "Move away from slopes and drainage channels.",
        "Watch for cracks, tilting trees and unusual ground movement.",
        "Avoid blocked roads and unstable debris.",
        "Evacuate early during heavy rainfall in landslide-prone areas.",
        "Do not cross an active landslide zone."
    ],
    "Heatwave":[
        "Drink water regularly.",
        "Avoid strenuous outdoor activity during peak heat.",
        "Wear light clothing and use shade.",
        "Check elderly people and children.",
        "Seek medical help for confusion, fainting or very high body temperature."
    ]
}
