import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.database import init_db, connect
from utils.logic import (
    incident_priority, ward_risk_score, shelter_occupancy_percent,
    shelter_status, resource_priority, nearest_shelters, PREPAREDNESS
)
from utils.services import ask_ai, get_weather

load_dotenv()
init_db()

APP_NAME = os.getenv("APP_NAME", "SurakshaSetu AI")
REGION_NAME = os.getenv("REGION_NAME", "Demo District")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
EOC_LAT = float(os.getenv("EOC_LAT", "26.1445"))
EOC_LON = float(os.getenv("EOC_LON", "91.7362"))
HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "70"))
CRITICAL_INCIDENT_THRESHOLD = float(os.getenv("CRITICAL_INCIDENT_THRESHOLD", "80"))
MAX_SHELTER_OCCUPANCY_ALERT = float(os.getenv("MAX_SHELTER_OCCUPANCY_ALERT", "90"))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title=APP_NAME, page_icon="🚨", layout="wide")

def df_query(sql, params=()):
    conn = connect()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = connect()
    conn.execute(sql, params)
    conn.commit()
    conn.close()

def refresh_priorities():
    incidents = df_query("SELECT * FROM incidents WHERE status!='Resolved'")
    for _, row in incidents.iterrows():
        score = incident_priority(
            row["disaster_type"], int(row["severity"]),
            int(row["people_affected"]), int(row["injured"]),
            int(row["trapped"]), row["created_at"]
        )
        execute(
            "UPDATE incidents SET priority_score=?, updated_at=? WHERE id=?",
            (score, datetime.now().isoformat(timespec="seconds"), int(row["id"]))
        )

refresh_priorities()

with st.sidebar:
    st.title(APP_NAME)
    st.caption(f"Disaster coordination for {REGION_NAME}")
    role = st.selectbox("Use as", ["Citizen", "Responder", "Admin"])

    citizen_pages = [
        "Citizen Home","Report Emergency","Find Shelter","Request Resources",
        "Missing Person","Preparedness Guide","Emergency AI Assistant"
    ]
    responder_pages = [
        "Responder Dashboard","Priority Incidents","Resource Requests",
        "Volunteer Coordination","Shelter Operations"
    ]
    admin_pages = [
        "Command Dashboard","Risk Hotspots","Incident Management",
        "Shelter Analytics","Weather Monitor","AI Command Advisor"
    ]

    pages = citizen_pages if role=="Citizen" else responder_pages if role=="Responder" else admin_pages
    page = st.radio("Navigation", pages)
    st.divider()
    st.caption("SQLite • optional AI • optional live weather")

if page == "Citizen Home":
    st.title(f"🚨 {APP_NAME}")
    st.subheader("Report fast. Respond smarter. Recover together.")
    active = int(df_query("SELECT COUNT(*) c FROM incidents WHERE status!='Resolved'").iloc[0]["c"])
    shelters = int(df_query("SELECT COUNT(*) c FROM shelters WHERE status='Open'").iloc[0]["c"])
    volunteers = int(df_query("SELECT COUNT(*) c FROM volunteers WHERE status='Available'").iloc[0]["c"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Active Incidents", active)
    c2.metric("Open Shelters", shelters)
    c3.metric("Available Volunteers", volunteers)
    st.error("For immediate danger, contact local emergency services and move to a safe place. This project supports coordination; it does not replace emergency responders.")
    st.markdown("### Available citizen services")
    st.write("• Emergency reporting\n• Nearest shelter search\n• Emergency resource requests\n• Missing-person registry\n• Preparedness guidance\n• AI/rule-based emergency assistant")

elif page == "Report Emergency":
    st.title("Report Emergency")
    with st.form("incident_form", clear_on_submit=True):
        c1,c2 = st.columns(2)
        with c1:
            reporter = st.text_input("Reporter Name")
            phone = st.text_input("Phone")
            disaster = st.selectbox("Disaster Type", ["Flood","Fire","Earthquake","Landslide","Cyclone","Storm","Heatwave","Other"])
            ward = st.selectbox("Ward / Zone", ["Ward 1","Ward 2","Ward 3","Ward 4","Ward 5"])
            location = st.text_input("Location / Landmark")
            lat = st.number_input("Latitude", value=EOC_LAT, format="%.6f")
            lon = st.number_input("Longitude", value=EOC_LON, format="%.6f")
        with c2:
            severity = st.slider("Severity",1,5,3)
            affected = st.number_input("People Affected",0,10000,1)
            injured = st.number_input("Injured",0,1000,0)
            trapped = st.number_input("People Trapped",0,1000,0)
            desc = st.text_area("Description")
            photo = st.file_uploader("Optional Photo", type=["jpg","jpeg","png"])

        if st.form_submit_button("Submit Emergency Report", use_container_width=True):
            if not reporter.strip() or not location.strip():
                st.error("Reporter name and location are required.")
            else:
                image_path = None
                if photo:
                    name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name.replace(' ','_')}"
                    p = UPLOAD_DIR/name
                    p.write_bytes(photo.getbuffer())
                    image_path = str(p)
                now = datetime.now().isoformat(timespec="seconds")
                score = incident_priority(disaster,severity,affected,injured,trapped,now)
                execute("""INSERT INTO incidents
                    (reporter_name,phone,disaster_type,location_text,ward,lat,lon,severity,
                     people_affected,injured,trapped,description,image_path,status,priority_score,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'Open',?,?,?)""",
                    (reporter,phone,disaster,location,ward,lat,lon,severity,affected,injured,trapped,desc,image_path,score,now,now))
                st.success(f"Emergency reported. Priority score: {score}/100")

elif page == "Find Shelter":
    st.title("Find Nearest Shelter")
    lat = st.number_input("Your Latitude", value=EOC_LAT, format="%.6f")
    lon = st.number_input("Your Longitude", value=EOC_LON, format="%.6f")
    if st.button("Find Nearest Shelters", use_container_width=True):
        shelters = df_query("SELECT * FROM shelters WHERE status='Open'")
        ranked = nearest_shelters(lat,lon,shelters.to_dict("records"))
        for s in ranked[:5]:
            with st.container(border=True):
                pct = shelter_occupancy_percent(int(s["occupied"]),int(s["capacity"]))
                status = shelter_status(int(s["occupied"]),int(s["capacity"]),MAX_SHELTER_OCCUPANCY_ALERT)
                st.markdown(f"### {s['name']}")
                a,b,c = st.columns(3)
                a.metric("Distance",f"{s['distance_km']:.2f} km")
                b.metric("Occupancy",f"{pct:.1f}%")
                c.metric("Status",status)
                st.write(s["address"])
                st.caption(f"Food: {s['food_units']} | Water: {s['water_units']} | Medical kits: {s['medical_kits']}")

elif page == "Request Resources":
    st.title("Request Emergency Resources")
    with st.form("resource_form", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            requester=st.text_input("Requester Name")
            phone=st.text_input("Phone")
            ward=st.selectbox("Ward / Zone",["Ward 1","Ward 2","Ward 3","Ward 4","Ward 5"])
            location=st.text_input("Location")
            lat=st.number_input("Latitude",value=EOC_LAT,format="%.6f")
            lon=st.number_input("Longitude",value=EOC_LON,format="%.6f")
        with c2:
            resource=st.selectbox("Resource Needed",["Rescue","Medical Help","Drinking Water","Food","Transport","Temporary Shelter","Baby Supplies","Other"])
            quantity=st.number_input("Quantity / People",1,10000,1)
            urgency=st.slider("Urgency",1,5,3)
        if st.form_submit_button("Submit Resource Request", use_container_width=True):
            if not requester.strip() or not location.strip():
                st.error("Requester name and location are required.")
            else:
                execute("""INSERT INTO resource_requests
                    (requester,phone,ward,resource_type,quantity,urgency,location_text,lat,lon,status,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,'Requested',?)""",
                    (requester,phone,ward,resource,quantity,urgency,location,lat,lon,datetime.now().isoformat(timespec="seconds")))
                st.success("Resource request submitted.")

elif page == "Missing Person":
    st.title("Missing Person Registry")
    with st.form("missing_form", clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            name=st.text_input("Missing Person Name")
            age=st.number_input("Age",0,120,18)
            gender=st.selectbox("Gender",["Male","Female","Other","Prefer not to say"])
            ward=st.selectbox("Ward / Zone",["Ward 1","Ward 2","Ward 3","Ward 4","Ward 5"])
            last_seen=st.text_input("Last Seen Location")
        with c2:
            contact=st.text_input("Contact Person")
            phone=st.text_input("Contact Phone")
            photo=st.file_uploader("Optional Photo",type=["jpg","jpeg","png"])
        if st.form_submit_button("Register Missing Person",use_container_width=True):
            if not name.strip() or not last_seen.strip() or not contact.strip():
                st.error("Please complete the required details.")
            else:
                photo_path=None
                if photo:
                    p=UPLOAD_DIR/f"missing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name.replace(' ','_')}"
                    p.write_bytes(photo.getbuffer())
                    photo_path=str(p)
                execute("""INSERT INTO missing_people
                    (name,age,gender,last_seen_location,ward,contact_person,contact_phone,photo_path,status,created_at)
                    VALUES (?,?,?,?,?,?,?,?,'Missing',?)""",
                    (name,age,gender,last_seen,ward,contact,phone,photo_path,datetime.now().isoformat(timespec="seconds")))
                st.success("Missing person entry created.")
    missing=df_query("SELECT * FROM missing_people WHERE status='Missing' ORDER BY created_at DESC")
    if not missing.empty:
        st.dataframe(missing[["id","name","age","gender","last_seen_location","ward","contact_person","contact_phone"]],use_container_width=True)

elif page == "Preparedness Guide":
    st.title("Disaster Preparedness Guide")
    disaster=st.selectbox("Select Disaster Type",list(PREPAREDNESS.keys()))
    for item in PREPAREDNESS[disaster]:
        st.write("•",item)
    st.divider()
    st.subheader("Basic Emergency Kit")
    st.write("• Drinking water\n• Dry food\n• Essential medicines\n• First-aid kit\n• Torch and batteries\n• Power bank\n• Copies of documents\n• Basic clothing and hygiene supplies")

elif page == "Emergency AI Assistant":
    st.title("Emergency AI Assistant")
    st.caption("Works without an API key; Groq is used when configured in .env.")
    q=st.text_area("Ask a disaster-management question",placeholder="What should I do if floodwater is rising near my house?")
    if st.button("Get Guidance",use_container_width=True):
        answer,mode=ask_ai(q,f"Region: {REGION_NAME}")
        st.warning(answer)
        st.caption(mode)

elif page == "Responder Dashboard":
    st.title("Responder Dashboard")
    incidents=df_query("SELECT * FROM incidents WHERE status!='Resolved'")
    resources=df_query("SELECT * FROM resource_requests WHERE status='Requested'")
    shelters=df_query("SELECT * FROM shelters WHERE status='Open'")
    critical=int((incidents["priority_score"]>=CRITICAL_INCIDENT_THRESHOLD).sum()) if not incidents.empty else 0
    a,b,c,d=st.columns(4)
    a.metric("Open Incidents",len(incidents))
    b.metric("Critical",critical)
    c.metric("Resource Requests",len(resources))
    d.metric("Open Shelters",len(shelters))
    if not incidents.empty:
        st.dataframe(incidents[["id","disaster_type","ward","location_text","people_affected","injured","trapped","priority_score","status"]].sort_values("priority_score",ascending=False).head(10),use_container_width=True)

elif page == "Priority Incidents":
    st.title("Priority Incident Queue")
    incidents=df_query("SELECT * FROM incidents WHERE status!='Resolved' ORDER BY priority_score DESC")
    for _,row in incidents.iterrows():
        with st.container(border=True):
            st.markdown(f"### #{int(row['id'])} — {row['disaster_type']} — {row['location_text']}")
            a,b,c,d=st.columns(4)
            a.metric("Priority",f"{float(row['priority_score']):.1f}")
            b.metric("Affected",int(row["people_affected"]))
            c.metric("Injured",int(row["injured"]))
            d.metric("Trapped",int(row["trapped"]))
            st.write(row["description"] or "No description")
            responder=st.text_input("Responder / Team Name",key=f"team_{int(row['id'])}")
            x,y=st.columns(2)
            with x:
                if st.button("Assign Team",key=f"assign_{int(row['id'])}",use_container_width=True):
                    if not responder.strip():
                        st.error("Enter team name.")
                    else:
                        execute("UPDATE incidents SET status='Assigned', updated_at=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),int(row["id"])))
                        execute("""INSERT INTO response_tasks
                            (incident_id,task_type,assigned_to,status,notes,created_at)
                            VALUES (?,'Incident Response',?,'Active',?,?)""",
                            (int(row["id"]),responder,f"{row['disaster_type']} at {row['location_text']}",datetime.now().isoformat(timespec="seconds")))
                        st.rerun()
            with y:
                if st.button("Mark Resolved",key=f"resolve_{int(row['id'])}",use_container_width=True):
                    execute("UPDATE incidents SET status='Resolved', updated_at=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),int(row["id"])))
                    st.rerun()

elif page == "Resource Requests":
    st.title("Emergency Resource Requests")
    req=df_query("SELECT * FROM resource_requests WHERE status='Requested'")
    if req.empty:
        st.success("No pending requests.")
    else:
        req["priority"]=req.apply(lambda r:resource_priority(int(r["urgency"]),int(r["quantity"]),r["created_at"]),axis=1)
        req=req.sort_values("priority",ascending=False)
        st.dataframe(req[["id","requester","ward","resource_type","quantity","urgency","location_text","priority"]],use_container_width=True)
        selected=st.selectbox("Request ID to fulfill",req["id"].astype(int).tolist())
        if st.button("Mark Fulfilled"):
            execute("UPDATE resource_requests SET status='Fulfilled' WHERE id=?",(int(selected),))
            st.rerun()

elif page == "Volunteer Coordination":
    st.title("Volunteer Coordination")
    with st.form("volunteer_form",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            name=st.text_input("Volunteer Name")
            phone=st.text_input("Phone")
            ward=st.selectbox("Ward",["Ward 1","Ward 2","Ward 3","Ward 4","Ward 5"])
        with c2:
            skills=st.text_input("Skills",placeholder="First Aid, Driving, Swimming...")
            availability=st.selectbox("Availability",["Morning","Afternoon","Evening","Full Day"])
        if st.form_submit_button("Register Volunteer",use_container_width=True):
            if not name.strip():
                st.error("Enter volunteer name.")
            else:
                execute("INSERT INTO volunteers (name,phone,ward,skills,availability,status) VALUES (?,?,?,?,?,'Available')",(name,phone,ward,skills,availability))
                st.rerun()
    st.dataframe(df_query("SELECT * FROM volunteers ORDER BY status,ward,name"),use_container_width=True)

elif page == "Shelter Operations":
    st.title("Shelter Operations")
    shelters=df_query("SELECT * FROM shelters ORDER BY ward,name")
    for _,row in shelters.iterrows():
        with st.container(border=True):
            pct=shelter_occupancy_percent(int(row["occupied"]),int(row["capacity"]))
            status=shelter_status(int(row["occupied"]),int(row["capacity"]),MAX_SHELTER_OCCUPANCY_ALERT)
            st.markdown(f"### {row['name']} — {row['ward']}")
            a,b,c,d=st.columns(4)
            a.metric("Occupancy",f"{row['occupied']}/{row['capacity']}")
            b.metric("Status",status)
            c.metric("Food Units",int(row["food_units"]))
            d.metric("Medical Kits",int(row["medical_kits"]))
            st.progress(min(pct/100,1.0))
            new_occ=st.number_input("Update Occupied",0,int(row["capacity"]),int(row["occupied"]),key=f"occ_{int(row['id'])}")
            if st.button("Update Shelter",key=f"upd_{int(row['id'])}"):
                execute("UPDATE shelters SET occupied=? WHERE id=?",(int(new_occ),int(row["id"])))
                st.rerun()

elif page == "Command Dashboard":
    st.title("Emergency Command Dashboard")
    password=st.text_input("Admin Password",type="password")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter the admin password configured in .env.")
        st.stop()
    incidents=df_query("SELECT * FROM incidents")
    active=incidents[incidents["status"]!="Resolved"].copy() if not incidents.empty else incidents
    shelters=df_query("SELECT * FROM shelters")
    critical=int((active["priority_score"]>=CRITICAL_INCIDENT_THRESHOLD).sum()) if not active.empty else 0
    affected=int(active["people_affected"].sum()) if not active.empty else 0
    trapped=int(active["trapped"].sum()) if not active.empty else 0
    a,b,c,d=st.columns(4)
    a.metric("Active Incidents",len(active))
    b.metric("Critical",critical)
    c.metric("People Affected",affected)
    d.metric("People Trapped",trapped)
    if not active.empty:
        t=active.groupby("disaster_type",as_index=False).size()
        st.plotly_chart(px.bar(t,x="disaster_type",y="size",text_auto=True),use_container_width=True)
        geo=active[["lat","lon"]].dropna()
        if not geo.empty:
            st.subheader("Incident Map")
            st.map(geo)
    if not shelters.empty:
        shelters["occupancy_percent"]=shelters.apply(lambda r:shelter_occupancy_percent(int(r["occupied"]),int(r["capacity"])),axis=1)
        st.plotly_chart(px.bar(shelters,x="name",y="occupancy_percent",text_auto=".1f"),use_container_width=True)

elif page == "Risk Hotspots":
    st.title("Ward Risk Hotspots")
    password=st.text_input("Admin Password",type="password",key="riskpass")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()
    active=df_query("SELECT * FROM incidents WHERE status!='Resolved'")
    if active.empty:
        st.success("No active risk hotspots.")
    else:
        active["is_severe"]=(active["severity"]>=4).astype(int)
        rows=[]
        for ward,group in active.groupby("ward"):
            avg=float(group["priority_score"].mean())
            score=ward_risk_score(len(group),int(group["is_severe"].sum()),int(group["people_affected"].sum()),int(group["trapped"].sum()),avg)
            rows.append({"ward":ward,"open_incidents":len(group),"severe_incidents":int(group["is_severe"].sum()),"people_affected":int(group["people_affected"].sum()),"trapped":int(group["trapped"].sum()),"avg_priority":round(avg,1),"risk_score":score,"risk_level":"HIGH" if score>=HIGH_RISK_THRESHOLD else "WATCH"})
        risk=pd.DataFrame(rows).sort_values("risk_score",ascending=False)
        st.dataframe(risk,use_container_width=True)
        st.plotly_chart(px.bar(risk,x="ward",y="risk_score",color="risk_level",text_auto=True),use_container_width=True)

elif page == "Incident Management":
    st.title("Incident Management")
    password=st.text_input("Admin Password",type="password",key="incpass")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()
    incidents=df_query("SELECT * FROM incidents ORDER BY priority_score DESC,created_at DESC")
    st.dataframe(incidents[["id","disaster_type","ward","location_text","severity","people_affected","injured","trapped","priority_score","status","created_at"]],use_container_width=True)

elif page == "Shelter Analytics":
    st.title("Shelter Analytics")
    password=st.text_input("Admin Password",type="password",key="shelpass")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()
    shelters=df_query("SELECT * FROM shelters")
    shelters["occupancy_percent"]=shelters.apply(lambda r:shelter_occupancy_percent(int(r["occupied"]),int(r["capacity"])),axis=1)
    shelters["load_status"]=shelters.apply(lambda r:shelter_status(int(r["occupied"]),int(r["capacity"]),MAX_SHELTER_OCCUPANCY_ALERT),axis=1)
    st.dataframe(shelters[["name","ward","capacity","occupied","occupancy_percent","food_units","water_units","medical_kits","load_status"]],use_container_width=True)

elif page == "Weather Monitor":
    st.title("Live Weather Monitor")
    password=st.text_input("Admin Password",type="password",key="weatherpass")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()
    weather=get_weather()
    if not weather.get("available"):
        st.info(weather["message"])
        st.caption("Set OPENWEATHER_API_KEY and WEATHER_CITY in .env to enable live data.")
    else:
        a,b,c,d=st.columns(4)
        a.metric("City",weather["city"])
        b.metric("Temperature",f"{weather['temperature']:.1f} °C")
        c.metric("Humidity",f"{weather['humidity']}%")
        d.metric("Wind Speed",f"{weather['wind_speed']} m/s")
        st.success(f"Condition: {weather['condition']}")

elif page == "AI Command Advisor":
    st.title("AI Command Advisor")
    password=st.text_input("Admin Password",type="password",key="aipass")
    if password!=ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()
    incidents=df_query("SELECT * FROM incidents WHERE status!='Resolved'")
    shelters=df_query("SELECT * FROM shelters")
    context=(
        f"Region: {REGION_NAME}. Active incidents: {len(incidents)}. "
        f"People affected: {int(incidents['people_affected'].sum()) if not incidents.empty else 0}. "
        f"Injured: {int(incidents['injured'].sum()) if not incidents.empty else 0}. "
        f"Trapped: {int(incidents['trapped'].sum()) if not incidents.empty else 0}. "
        f"Open shelters: {int((shelters['status']=='Open').sum()) if not shelters.empty else 0}."
    )
    q=st.text_area("Ask the command advisor",placeholder="What should the response team prioritize right now?")
    if st.button("Generate Response Advice",use_container_width=True):
        answer,mode=ask_ai(q,context)
        st.warning(answer)
        st.caption(mode)
