import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("data/suraksha.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_name TEXT NOT NULL,
        phone TEXT,
        disaster_type TEXT NOT NULL,
        location_text TEXT NOT NULL,
        ward TEXT NOT NULL,
        lat REAL,
        lon REAL,
        severity INTEGER NOT NULL,
        people_affected INTEGER DEFAULT 0,
        injured INTEGER DEFAULT 0,
        trapped INTEGER DEFAULT 0,
        description TEXT,
        image_path TEXT,
        status TEXT DEFAULT 'Open',
        priority_score REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS shelters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ward TEXT NOT NULL,
        address TEXT NOT NULL,
        lat REAL,
        lon REAL,
        capacity INTEGER NOT NULL,
        occupied INTEGER DEFAULT 0,
        food_units INTEGER DEFAULT 0,
        water_units INTEGER DEFAULT 0,
        medical_kits INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Open'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS resource_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester TEXT NOT NULL,
        phone TEXT,
        ward TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        urgency INTEGER NOT NULL,
        location_text TEXT NOT NULL,
        lat REAL,
        lon REAL,
        status TEXT DEFAULT 'Requested',
        created_at TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        ward TEXT NOT NULL,
        skills TEXT,
        availability TEXT,
        status TEXT DEFAULT 'Available'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS response_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER,
        task_type TEXT NOT NULL,
        assigned_to TEXT,
        status TEXT DEFAULT 'Pending',
        notes TEXT,
        created_at TEXT NOT NULL,
        completed_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS missing_people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        last_seen_location TEXT NOT NULL,
        ward TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        contact_phone TEXT,
        photo_path TEXT,
        status TEXT DEFAULT 'Missing',
        created_at TEXT NOT NULL
    )""")

    conn.commit()

    if cur.execute("SELECT COUNT(*) FROM shelters").fetchone()[0] == 0:
        seed_demo_data(conn)

    conn.close()

def seed_demo_data(conn):
    cur = conn.cursor()
    now = datetime.now()

    shelters = [
        ("Govt. Higher Secondary School","Ward 1","Main Road, Ward 1",26.1455,91.7354,300,85,260,230,28,"Open"),
        ("Community Hall","Ward 2","Market Road, Ward 2",26.1439,91.7382,180,120,140,130,18,"Open"),
        ("Primary Health Centre Annex","Ward 3","PHC Campus, Ward 3",26.1478,91.7391,120,70,90,95,35,"Open"),
        ("College Auditorium","Ward 4","College Road, Ward 4",26.1490,91.7335,400,210,350,310,42,"Open")
    ]
    cur.executemany("""INSERT INTO shelters
        (name,ward,address,lat,lon,capacity,occupied,food_units,water_units,medical_kits,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", shelters)

    incidents = [
        ("Rupam","9000000011","Flood","Riverside settlement","Ward 2",26.1432,91.7388,5,90,6,4,"Water level rising rapidly and several houses are surrounded."),
        ("Mitali","9000000012","Landslide","Hill road turn","Ward 3",26.1483,91.7400,4,25,3,1,"Road partially blocked by soil and rocks."),
        ("Imran","9000000013","Fire","Market lane","Ward 1",26.1460,91.7349,5,40,5,2,"Fire spreading between nearby shops."),
        ("Anita","9000000014","Storm","School colony","Ward 4",26.1493,91.7330,3,35,1,0,"Trees and electric poles damaged after strong wind.")
    ]
    bonuses = {"Fire":22,"Flood":18,"Landslide":20,"Earthquake":24}
    for i, row in enumerate(incidents):
        created = now - timedelta(hours=(i+1)*4)
        severity, affected, injured, trapped = row[7], row[8], row[9], row[10]
        age_hours = (now-created).total_seconds()/3600
        priority = min(100, severity*9 + affected*0.08 + injured*2.8 + trapped*5 + age_hours*0.45 + bonuses.get(row[2],8))
        cur.execute("""INSERT INTO incidents
            (reporter_name,phone,disaster_type,location_text,ward,lat,lon,severity,
             people_affected,injured,trapped,description,image_path,status,priority_score,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,NULL,'Open',?,?,?)""",
            (*row, priority, created.isoformat(timespec="seconds"), created.isoformat(timespec="seconds")))

    volunteers = [
        ("Rahul Das","9001000011","Ward 1","First Aid, Driving","Full Day","Available"),
        ("Naina Bora","9001000012","Ward 2","Nursing, Child Care","Morning","Available"),
        ("Amit Ali","9001000013","Ward 3","Boat Handling, Swimming","Full Day","Available"),
        ("Puja Nath","9001000014","Ward 4","Food Distribution, Data Entry","Evening","Available")
    ]
    cur.executemany("""INSERT INTO volunteers
        (name,phone,ward,skills,availability,status) VALUES (?,?,?,?,?,?)""", volunteers)
    conn.commit()
