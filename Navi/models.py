from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(64), unique=True, nullable=False)
    pw_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'user' or 'admin'

    def set_password(self, pw): self.pw_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.pw_hash, pw)

class Hazard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

class SafeHouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, default=10)
    occupied = db.Column(db.Integer, default=0)

    @property
    def available(self): return max(self.capacity - self.occupied, 0)

class Poi(db.Model):
    """Other village landmarks: schools/shops/parks/temples/houses."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(32), nullable=False)  # school/shop/park/temple/house
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)

class PathHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    safehouse_id = db.Column(db.Integer, db.ForeignKey("safe_house.id"))
    start_x = db.Column(db.Integer)
    start_y = db.Column(db.Integer)
    dest_x = db.Column(db.Integer)
    dest_y = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    group_size = db.Column(db.Integer, default=1)
    path_json = db.Column(db.Text)          # JSON list of coords
    instructions = db.Column(db.Text)       # text directions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Stay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    safehouse_id = db.Column(db.Integer, db.ForeignKey("safe_house.id"))
    group_size = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
