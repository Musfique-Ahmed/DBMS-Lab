import datetime
import math
from typing import List, Optional, Tuple
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from . import models, database

# Create all database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Safe Route API",
    description="API for suggesting safe travel routes and providing emergency alerts.",
    version="2.0.0"
)

# CORS configuration remains the same

# --- Pydantic Models ---
class PanicRequest(BaseModel):
    user_id: int
    lat: float
    lon: float

class RouteRequest(BaseModel):
    # ... (existing RouteRequest model)

# --- Helper Functions ---
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers."""
    R = 6371  # Radius of Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- New Endpoints for Panic Mode ---

@app.post("/panic")
async def trigger_panic_mode(request: PanicRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Log the panic event
    new_alert = models.PanicAlert(
        user_id=user.id,
        latitude=request.lat,
        longitude=request.lon
    )
    db.add(new_alert)
    db.commit()

    # Find nearby friends (1st degree)
    nearby_friends = []
    alert_radius_km = 5.0 # Notify friends within 5km

    for friend in user.friends:
        if friend.last_known_lat and friend.last_known_lon:
            distance = haversine_distance(request.lat, request.lon, friend.last_known_lat, friend.last_known_lon)
            if distance <= alert_radius_km:
                nearby_friends.append(friend)

    # If friends are nearby, notify them
    notified_users = set()
    if nearby_friends:
        for friend in nearby_friends:
            message = f"PANIC ALERT: Your friend {user.username} is in distress near your location!"
            notification = models.Notification(user_id=friend.id, message=message)
            db.add(notification)
            notified_users.add(friend.id)
    else:
        # If no friends nearby, check friends of friends (2nd degree)
        for friend in user.friends:
            for friend_of_friend in friend.friends:
                # Avoid notifying the original user or already notified users
                if friend_of_friend.id == user.id or friend_of_friend.id in notified_users:
                    continue
                
                if friend_of_friend.last_known_lat and friend_of_friend.last_known_lon:
                    distance = haversine_distance(request.lat, request.lon, friend_of_friend.last_known_lat, friend_of_friend.last_known_lon)
                    if distance <= alert_radius_km:
                        message = f"PANIC ALERT: {user.username} (friend of {friend.username}) is in distress near you!"
                        notification = models.Notification(user_id=friend_of_friend.id, message=message)
                        db.add(notification)
                        notified_users.add(friend_of_friend.id)

    db.commit()
    return {"message": "Panic alert sent!", "notified_count": len(notified_users)}

@app.get("/notifications/{user_id}")
async def get_notifications(user_id: int, db: Session = Depends(database.get_db)):
    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).order_by(models.Notification.timestamp.desc()).all()
    
    # Mark them as read after fetching
    for notif in notifications:
        notif.is_read = True
    db.commit()
    
    return [{"id": n.id, "message": n.message, "time": n.timestamp.isoformat()} for n in notifications]


# --- Existing /suggest-route endpoint ---
# The code for /suggest-route remains the same as the last version.
# ...
# You would add placeholder endpoints for registration and contact sync here.

