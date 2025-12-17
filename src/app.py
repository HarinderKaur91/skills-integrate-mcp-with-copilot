"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from .models import Base, Activity, Participant
except ImportError:
    from models import Base, Activity, Participant

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Seed data (used to initialize the database if empty)
seed_activities = {
    # Technical Activities
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "category": "technical"
    },
    "Robotics Club": {
        "description": "Build and program robots for competitions",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "lucas@mergington.edu"]
    },
    "Web Development Workshop": {
        "description": "Learn HTML, CSS, and JavaScript to build websites",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 16,
        "participants": ["jordan@mergington.edu"]
    },
    "AI and Machine Learning Club": {
        "description": "Explore artificial intelligence and machine learning applications",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["maya@mergington.edu", "ryan@mergington.edu"]
    },
    "Cybersecurity Club": {
        "description": "Learn about cybersecurity, hacking prevention, and ethical hacking",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["tyler@mergington.edu"]
    },
    "Game Development Club": {
        "description": "Create games using game engines like Unity or Unreal",
        "schedule": "Tuesdays, 4:30 PM - 6:00 PM",
        "max_participants": 14,
        "participants": ["mason@mergington.edu", "ethan@mergington.edu"]
    },
    "Data Science Club": {
        "description": "Analyze data and create visualizations using Python",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["zoe@mergington.edu"]
    },
    
    # Non-Technical Activities
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "category": "non-technical"
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "category": "non-technical"
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "category": "non-technical"
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "category": "non-technical"
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "category": "non-technical"
    },
    "Music Band": {
        "description": "Play musical instruments and perform at school events",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["grace@mergington.edu", "olivia@mergington.edu"]
    },
    "Choir": {
        "description": "Sing together and perform at concerts",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 30,
        "participants": ["isabella@mergington.edu", "victoria@mergington.edu"]
    },
    "Photography Club": {
        "description": "Learn photography techniques and exhibit your work",
        "schedule": "Saturdays, 2:00 PM - 4:00 PM",
        "max_participants": 12,
        "participants": ["lucas@mergington.edu"]
    },
    "Model United Nations": {
        "description": "Debate global issues and represent countries in mock UN sessions",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["nathan@mergington.edu", "olivia@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["marcus@mergington.edu"]
    },
    
    # Sports Activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "category": "sports"
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "category": "sports"
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "category": "sports"
    },
    "Football Team": {
        "description": "Play American football and compete in league matches",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["marcus@mergington.edu", "tyler@mergington.edu"]
    },
    "Volleyball Team": {
        "description": "Learn volleyball skills and compete against other schools",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["jessica@mergington.edu", "emily@mergington.edu"]
    },
    "Tennis Team": {
        "description": "Master tennis skills and participate in tournaments",
        "schedule": "Mondays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["andrew@mergington.edu"]
    },
    "Track and Field": {
        "description": "Run, jump, and throw to compete in track events",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["jessica@mergington.edu", "david@mergington.edu"]
    },
    "Swimming Team": {
        "description": "Swim competitively and improve your technique",
        "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["sophia@mergington.edu", "daniel@mergington.edu"]
    },
    "Badminton Club": {
        "description": "Play badminton recreationally and competitively",
        "schedule": "Saturdays, 2:00 PM - 4:00 PM",
        "max_participants": 10,
        "participants": ["kevin@mergington.edu"]
    },
    "Martial Arts Club": {
        "description": "Learn karate, taekwondo, and self-defense techniques",
        "schedule": "Thursdays and Saturdays, 5:00 PM - 6:30 PM",
        "max_participants": 18,
        "participants": ["christopher@mergington.edu", "jacob@mergington.edu"]
    }
}

# Setup SQLite engine and session
DB_PATH = os.path.join(current_dir, "activities.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed DB if empty
def seed_database():
    session = SessionLocal()
    try:
        any_activity = session.query(Activity).first()
        if any_activity is None:
            for name, info in seed_activities.items():
                act = Activity(name=name, description=info.get("description"), schedule=info.get("schedule"), max_participants=info.get("max_participants"), category=info.get("category"))
                session.add(act)
                session.flush()
                for email in info.get("participants", []):
                    p = Participant(email=email, activity_id=act.id)
                    session.add(p)
            session.commit()
    finally:
        session.close()

seed_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(category: str = None):
    session = SessionLocal()
    try:
        query = session.query(Activity)
        if category:
            query = query.filter(Activity.category == category)
        activities_list = {}
        for act in query.all():
            participants = [p.email for p in act.participants]
            activities_list[act.name] = {
                "description": act.description,
                "schedule": act.schedule,
                "max_participants": act.max_participants,
                "participants": participants,
                "category": act.category,
            }
        return activities_list
    finally:
        session.close()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    session = SessionLocal()
    try:
        act = session.query(Activity).filter(Activity.name == activity_name).first()
        if act is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        current_count = session.query(Participant).filter(Participant.activity_id == act.id).count()
        if any(p.email == email for p in act.participants):
            raise HTTPException(status_code=400, detail="Student is already signed up")

        if act.max_participants is not None and current_count >= act.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        participant = Participant(email=email, activity_id=act.id)
        session.add(participant)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        session.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    session = SessionLocal()
    try:
        act = session.query(Activity).filter(Activity.name == activity_name).first()
        if act is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = session.query(Participant).filter(Participant.activity_id == act.id, Participant.email == email).first()
        if participant is None:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        session.close()
