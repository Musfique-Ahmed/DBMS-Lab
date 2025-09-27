from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from models import *
from database import get_db

app = FastAPI(title="My Safety Admin API", version="1.0.0")

# ==================== CRIME MANAGEMENT ====================

@app.post("/api/crimes")
async def create_crime(crime_data: dict, db: Session = Depends(get_db)):
    """Create a new crime with all related information"""
    try:
        # Create location first
        location = Location(
            district_id=crime_data["location"]["district_id"],
            area_name=crime_data["location"]["area_name"],
            city=crime_data["location"]["city"],
            latitude=crime_data["location"]["latitude"],
            longitude=crime_data["location"]["longitude"],
            created_at=datetime.datetime.utcnow()
        )
        db.add(location)
        db.flush()  # Get the location_id
        
        # Create crime
        crime = Crime(
            crime_type=crime_data["crime"]["crime_type"],
            description=crime_data["crime"]["description"],
            date_time=datetime.datetime.fromisoformat(crime_data["crime"]["date_time"]),
            location_id=location.location_id,
            status=crime_data["crime"]["status"],
            created_at=datetime.datetime.utcnow()
        )
        db.add(crime)
        db.flush()  # Get the crime_id
        
        # Create victim if provided
        if crime_data.get("victim", {}).get("full_name"):
            victim = Victim(
                full_name=crime_data["victim"]["full_name"],
                dob=datetime.datetime.fromisoformat(crime_data["victim"]["dob"]) if crime_data["victim"].get("dob") else None,
                gender=crime_data["victim"].get("gender"),
                address=crime_data["victim"].get("address"),
                phone_number=crime_data["victim"].get("phone_number"),
                email=crime_data["victim"].get("email"),
                injury_details=crime_data["victim"].get("injury_details"),
                created_at=datetime.datetime.utcnow()
            )
            db.add(victim)
            db.flush()
            
            # Create crime-victim relationship
            crime_victim = CrimeVictim(
                crime_id=crime.crime_id,
                victim_id=victim.victim_id,
                injury_level="minor"  # Default, can be updated
            )
            db.add(crime_victim)
        
        # Create criminal if provided
        if crime_data.get("criminal", {}).get("full_name"):
            criminal = Criminal(
                full_name=crime_data["criminal"]["full_name"],
                alias_name=crime_data["criminal"].get("alias_name"),
                dob=datetime.datetime.fromisoformat(crime_data["criminal"]["dob"]) if crime_data["criminal"].get("dob") else None,
                gender=crime_data["criminal"].get("gender"),
                address=crime_data["criminal"].get("address"),
                marital_status=crime_data["criminal"].get("marital_status"),
                previous_crimes=crime_data["criminal"].get("previous_crimes"),
                created_at=datetime.datetime.utcnow()
            )
            db.add(criminal)
            db.flush()
            
            # Create crime-criminal relationship
            crime_criminal = CrimeCriminal(
                crime_id=crime.crime_id,
                criminal_id=criminal.criminal_id,
                notes="Initial report"
            )
            db.add(crime_criminal)
        
        # Create weapon if provided
        if crime_data.get("weapon", {}).get("weapon_name"):
            weapon = Weapon(
                weapon_name=crime_data["weapon"]["weapon_name"],
                weapon_type=crime_data["weapon"].get("weapon_type"),
                description=crime_data["weapon"].get("description"),
                serial_number=crime_data["weapon"].get("serial_number"),
                created_at=datetime.datetime.utcnow()
            )
            db.add(weapon)
            db.flush()
            
            # Create crime-weapon relationship
            crime_weapon = CrimeWeapon(
                crime_id=crime.crime_id,
                weapon_id=weapon.weapon_id,
                usage_detail="Used in crime"
            )
            db.add(crime_weapon)
        
        # Create witness if provided
        if crime_data.get("witness", {}).get("full_name"):
            witness = Witness(
                full_name=crime_data["witness"]["full_name"],
                phone_number=crime_data["witness"].get("phone_number"),
                protection_flag=crime_data["witness"].get("protection_flag", False)
            )
            db.add(witness)
            db.flush()
            
            # Create crime-witness relationship
            crime_witness = CrimeWitness(
                crime_id=crime.crime_id,
                witness_id=witness.witness_id,
                statement_status="pending"
            )
            db.add(crime_witness)
        
        db.commit()
        return {"message": "Crime created successfully", "crime_id": crime.crime_id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/crimes")
async def get_crimes(db: Session = Depends(get_db)):
    """Get all crimes with related information"""
    crimes = db.query(Crime).all()
    return crimes

@app.get("/api/crimes/{crime_id}")
async def get_crime(crime_id: int, db: Session = Depends(get_db)):
    """Get a specific crime by ID"""
    crime = db.query(Crime).filter(Crime.crime_id == crime_id).first()
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")
    return crime

# ==================== COMPLAINT MANAGEMENT ====================

@app.get("/api/complaints")
async def get_complaints(db: Session = Depends(get_db)):
    """Get all complaints"""
    complaints = db.query(Complaint).all()
    return complaints

@app.post("/api/complaints/{complaint_id}/verify")
async def verify_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Verify a complaint"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "verified"
    db.commit()
    return {"message": "Complaint verified successfully"}

@app.post("/api/complaints/{complaint_id}/reject")
async def reject_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Reject a complaint"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "rejected"
    db.commit()
    return {"message": "Complaint rejected successfully"}

@app.post("/api/complaints/{complaint_id}/escalate")
async def escalate_complaint_to_crime(complaint_id: int, crime_data: dict, db: Session = Depends(get_db)):
    """Escalate a complaint to a crime report"""
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Create crime from complaint
    crime = Crime(
        crime_type=crime_data.get("crime_type", "unknown"),
        description=complaint.description,
        date_time=complaint.reported_at,
        status="reported",
        created_at=datetime.datetime.utcnow()
    )
    db.add(crime)
    db.commit()
    
    # Update complaint status
    complaint.status = "escalated"
    db.commit()
    
    return {"message": "Complaint escalated to crime successfully", "crime_id": crime.crime_id}

# ==================== CASE ASSIGNMENT MANAGEMENT ====================

@app.get("/api/case-assignments")
async def get_case_assignments(db: Session = Depends(get_db)):
    """Get all case assignments"""
    assignments = db.query(CaseAssignment).all()
    return assignments

@app.post("/api/case-assignments")
async def create_case_assignment(assignment_data: dict, db: Session = Depends(get_db)):
    """Create a new case assignment"""
    assignment = CaseAssignment(
        user_id=assignment_data["user_id"],
        crime_id=assignment_data["crime_id"],
        duty_role=assignment_data["duty_role"],
        assigned_at=datetime.datetime.utcnow()
    )
    db.add(assignment)
    db.commit()
    return {"message": "Case assigned successfully", "assignment_id": assignment.assignment_id}

@app.put("/api/case-assignments/{assignment_id}")
async def update_case_assignment(assignment_id: int, assignment_data: dict, db: Session = Depends(get_db)):
    """Update a case assignment"""
    assignment = db.query(CaseAssignment).filter(CaseAssignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.duty_role = assignment_data.get("duty_role", assignment.duty_role)
    assignment.released_at = assignment_data.get("released_at")
    db.commit()
    return {"message": "Assignment updated successfully"}

# ==================== CASE STATUS HISTORY ====================

@app.get("/api/crimes/{crime_id}/status-history")
async def get_status_history(crime_id: int, db: Session = Depends(get_db)):
    """Get status history for a crime"""
    history = db.query(CaseStatusHistory).filter(CaseStatusHistory.crime_id == crime_id).all()
    return history

@app.post("/api/crimes/{crime_id}/status")
async def update_crime_status(crime_id: int, status_data: dict, db: Session = Depends(get_db)):
    """Update crime status and add to history"""
    crime = db.query(Crime).filter(Crime.crime_id == crime_id).first()
    if not crime:
        raise HTTPException(status_code=404, detail="Crime not found")
    
    # Update crime status
    old_status = crime.status
    crime.status = status_data["new_status"]
    
    # Add to status history
    status_history = CaseStatusHistory(
        crime_id=crime_id,
        status=status_data["new_status"],
        notes=status_data.get("notes", ""),
        changed_at=datetime.datetime.utcnow(),
        changed_by=status_data["changed_by"]
    )
    db.add(status_history)
    db.commit()
    
    return {"message": f"Status updated from {old_status} to {status_data['new_status']}"}

# ==================== EVIDENCE MANAGEMENT ====================

@app.post("/api/crimes/{crime_id}/evidence")
async def add_evidence(crime_id: int, evidence_data: dict, db: Session = Depends(get_db)):
    """Add evidence to a crime"""
    evidence = Evidence(
        crime_id=crime_id,
        evidence_type=evidence_data["evidence_type"],
        storage_ref=evidence_data.get("storage_ref"),
        notes=evidence_data.get("notes"),
        collected_at=datetime.datetime.utcnow(),
        collected_by=evidence_data["collected_by"]
    )
    db.add(evidence)
    db.commit()
    return {"message": "Evidence added successfully", "evidence_id": evidence.evidence_id}

@app.get("/api/crimes/{crime_id}/evidence")
async def get_evidence(crime_id: int, db: Session = Depends(get_db)):
    """Get all evidence for a crime"""
    evidence = db.query(Evidence).filter(Evidence.crime_id == crime_id).all()
    return evidence

# ==================== ARREST MANAGEMENT ====================

@app.post("/api/arrests")
async def create_arrest(arrest_data: dict, db: Session = Depends(get_db)):
    """Create a new arrest record"""
    arrest = Arrest(
        criminal_id=arrest_data["criminal_id"],
        arrest_time=datetime.datetime.fromisoformat(arrest_data["arrest_time"]),
        officer_id=arrest_data["officer_id"],
        location_detail=arrest_data.get("location_detail")
    )
    db.add(arrest)
    db.flush()
    
    # Add charges if provided
    if arrest_data.get("charges"):
        for charge_data in arrest_data["charges"]:
            charge = Charge(
                arrest_id=arrest.arrest_id,
                legal_code=charge_data["legal_code"],
                description=charge_data["description"],
                disposition=charge_data.get("disposition", "pending")
            )
            db.add(charge)
    
    db.commit()
    return {"message": "Arrest created successfully", "arrest_id": arrest.arrest_id}

# ==================== USER MANAGEMENT ====================

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(AppUser).all()
    return users

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user"""
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ==================== LOCATION MANAGEMENT ====================

@app.get("/api/locations")
async def get_locations(db: Session = Depends(get_db)):
    """Get all locations"""
    locations = db.query(Location).all()
    return locations

@app.get("/api/districts")
async def get_districts(db: Session = Depends(get_db)):
    """Get all districts"""
    districts = db.query(District).all()
    return districts

# ==================== POLICE STATION MANAGEMENT ====================

@app.get("/api/police-stations")
async def get_police_stations(db: Session = Depends(get_db)):
    """Get all police stations"""
    stations = db.query(PoliceStation).all()
    return stations

@app.get("/api/police-stations/{station_id}/staff")
async def get_station_staff(station_id: int, db: Session = Depends(get_db)):
    """Get staff for a specific police station"""
    staff = db.query(StationStaff).filter(StationStaff.station_id == station_id).all()
    return staff

# ==================== PANIC EVENT MANAGEMENT ====================

@app.get("/api/panic-events")
async def get_panic_events(db: Session = Depends(get_db)):
    """Get all panic events"""
    events = db.query(PanicEvent).all()
    return events

@app.post("/api/panic-events/{panic_id}/notify")
async def send_panic_notification(panic_id: int, notification_data: dict, db: Session = Depends(get_db)):
    """Send notification for a panic event"""
    notification = PanicNotification(
        panic_id=panic_id,
        sender_id=notification_data["sender_id"],
        receiver_id=notification_data["receiver_id"],
        message=notification_data["message"],
        delivered=False
    )
    db.add(notification)
    db.commit()
    return {"message": "Notification sent successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
