from __future__ import annotations
import json
from flask import jsonify

from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, jsonify,session
)
from Navi.models import db, User, Hazard, SafeHouse, Poi, PathHistory, Stay
from Navi.utils import GRID_W, GRID_H, astar, path_to_instructions
import Navi.config as cfg
import session_config  # ✅ shared config


# ---------- Basic Flask Setup ----------
BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

app.config.from_object(session_config)
app.config.from_object(cfg)
db.init_app(app)


# ---------- One-Time Database Setup ----------
def setup_db():
    db.create_all()

    def ensure_user(username, password, role="user"):
        u = User.query.filter_by(username=username).first()
        if not u:
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
        return u

    def ensure_safehouse(name, x, y, capacity):
        s = SafeHouse.query.filter_by(name=name).first()
        if not s:
            s = SafeHouse(name=name, x=x, y=y, capacity=capacity, occupied=0)
            db.session.add(s)
            db.session.commit()
        return s

    def ensure_poi(name, ptype, x, y):
        p = Poi.query.filter_by(name=name).first()
        if not p:
            p = Poi(name=name, type=ptype, x=x, y=y)
            db.session.add(p)
            db.session.commit()
        return p

    def ensure_hazard(x, y, active=True):
        h = Hazard.query.filter_by(x=x, y=y).first()
        if not h:
            h = Hazard(x=x, y=y, active=active)
            db.session.add(h)
            db.session.commit()
        return h

    ensure_user("admin", "admin123", "admin")
    ensure_user("user1", "user123", "user")

 # ---------- grid content (idempotent) ----------
    # Safehouses (3)
    ensure_safehouse("Shelter A", 2, 3, 8)
    ensure_safehouse("Shelter B", 10, 5, 12)
    ensure_safehouse("Shelter C", 16, 14, 10)

    # School (1)
    ensure_poi("Govt School", "school", 5, 5)

    # Temples (2)
    ensure_poi("Temple 1", "temple", 10, 3)
    ensure_poi("Temple 2", "temple", 22, 20)

    # Shops (4)
    shops = [("Shop 1", 8, 12), ("Shop 2", 14, 7), ("Shop 3", 20, 9), ("Shop 4", 26, 15)]
    for name, x, y in shops:
        ensure_poi(name, "shop", x, y)

    # Houses (14)
    houses = [
        ("House 101", 3, 6), ("House 102", 6, 18), ("House 103", 9, 22), ("House 104", 12, 10),
        ("House 105", 15, 4), ("House 106", 18, 26), ("House 107", 21, 8), ("House 108", 24, 14),
        ("House 109", 27, 21), ("House 110", 29, 5), ("House 111", 4, 24), ("House 112", 11, 16),
        ("House 113", 16, 19), ("House 114", 25, 9),
    ]
    for name, x, y in houses:
        ensure_poi(name, "house", x, y)

    
    ensure_hazard(15, 14, True)
    ensure_hazard(11, 9, True)
    ensure_hazard(18, 17, True)


with app.app_context():
    setup_db()


# ---------- USER ----------
@app.get("/")
def home_redirect():
    """Directly open the map (no login required)."""
    return redirect("/navi/map")


@app.get("/map")
def user_map():
    """Disaster Management Map — now public access."""
    hazards = [{"x": h.x, "y": h.y} for h in Hazard.query.filter_by(active=True)]
    sh = SafeHouse.query.all()
    safehouses = [
        {"id": s.id, "name": s.name, "x": s.x, "y": s.y,
         "capacity": s.capacity, "occupied": s.occupied, "available": s.available}
        for s in sh
    ]
    pois = [{"name": p.name, "type": p.type, "x": p.x, "y": p.y} for p in Poi.query.all()]

    return render_template(
        "index.html",
        username="Guest User",
        width=GRID_W, height=GRID_H,
        hazards=hazards,
        safehouses=safehouses,
        pois=pois
    )


# ---------- Safehouse API ----------
@app.post("/api/route_to_safehouse")
def api_route_to_safehouse():
    """Public access — find safe route."""
    data = request.get_json(force=True)
    start = tuple(map(int, data["start"]))
    group_size = int(data.get("group_size", 1))

    blocked = {(h.x, h.y) for h in Hazard.query.filter_by(active=True)} | {
        (p.x, p.y) for p in Poi.query.filter(Poi.type.in_(['house', 'shop', 'temple', 'school']))
    }
    candidates = [s for s in SafeHouse.query.all() if s.available >= group_size]

    best, best_path = None, None
    for s in candidates:
        path = astar(start, (s.x, s.y), blocked)
        if path and (best_path is None or len(path) < len(best_path)):
            best, best_path = s, path

    if not best_path:
        return jsonify({"ok": False, "message": "No reachable safehouse."})

    instr = path_to_instructions(best_path)
    return jsonify({
        "ok": True,
        "safehouse": {
            "id": best.id,
            "name": best.name,
            "x": best.x,
            "y": best.y,
            "capacity": best.capacity,
            "occupied": best.occupied,
            "available": best.available
        },
        "path": best_path,
        "steps": len(best_path),
        "instructions": instr
    })


@app.post("/api/arrive")
def api_arrive():
    """Mark arrival — public (guest use)."""
    data = request.get_json(force=True)
    path = data["path"]
    safehouse_id = int(data["safehouse_id"])
    group_size = int(data.get("group_size", 1))

    s = SafeHouse.query.get(safehouse_id)
    if not s:
        return jsonify({"ok": False, "message": "Safehouse not found"})
    if s.available < group_size:
        return jsonify({"ok": False, "message": "Capacity full"})

    s.occupied += group_size
    db.session.commit()
    return jsonify({
        "ok": True,
        "message": "Checked in at safehouse",
        "available": s.available
    })


@app.post("/api/checkout")
def api_checkout():
    """Check out — public (guest use)."""
    data = request.get_json(force=True)
    safehouse_id = int(data.get("safehouse_id", 0)) or None
    group_size = int(data.get("group_size", 1))  # ✅ read group size from request

    s = SafeHouse.query.get(safehouse_id)
    if not s:
        return jsonify({"ok": False, "message": "Safehouse not found"})

    # ✅ Subtract the entire group size
    s.occupied = max(0, s.occupied - group_size)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": f"Checked out {group_size} member(s) successfully",
        "available": s.available,
        "safehouse_id": s.id
    })


# ---------- ADMIN ----------
@app.get("/admin")
def admin_dashboard():
    """Admin-only route (can protect later if needed)."""
    sh = SafeHouse.query.all()
    hz = Hazard.query.filter_by(active=True).all()
    pois = Poi.query.all()

    return render_template(
        "admin_dashboard.html",
        username=session.get("username", "Admin"),
        width=GRID_W,
        height=GRID_H,
        safehouses_json=json.dumps([{
            "id": s.id, "name": s.name, "x": s.x, "y": s.y,
            "capacity": s.capacity, "occupied": s.occupied, "available": s.available
        } for s in sh]),
        hazards_json=json.dumps([{"x": h.x, "y": h.y, "active": h.active} for h in hz]),
        pois_json=json.dumps([{"name": p.name, "type": p.type, "x": p.x, "y": p.y} for p in pois])
    )


# ---------------------- ADMIN API ROUTES ----------------------
@app.post("/admin/api/toggle_hazard")
def api_toggle_hazard():
    """Toggle hazard at a given (x, y) location."""
    data = request.get_json(force=True)
    x, y = int(data.get("x")), int(data.get("y"))

    hazard = Hazard.query.filter_by(x=x, y=y).first()
    if hazard:
        # Toggle off
        db.session.delete(hazard)
        db.session.commit()
        return jsonify({"ok": True, "active": False})
    else:
        # Add new hazard
        new_hazard = Hazard(x=x, y=y, active=True)
        db.session.add(new_hazard)
        db.session.commit()
        return jsonify({"ok": True, "active": True})


@app.post("/admin/api/set_capacity")
def api_set_capacity():
    """Set a safehouse's capacity."""
    data = request.get_json(force=True)
    sid = int(data.get("safehouse_id"))
    new_cap = int(data.get("capacity", 0))

    s = SafeHouse.query.get(sid)
    if not s:
        return jsonify({"ok": False, "error": "Safehouse not found"}), 404

    s.capacity = new_cap
    db.session.commit()
    return jsonify({
        "ok": True,
        "occupied": s.occupied,
        "available": s.capacity - s.occupied
    })


@app.post("/admin/api/reset_safehouse")
def api_reset_safehouse():
    """Reset a safehouse's occupancy count."""
    data = request.get_json(force=True)
    sid = int(data.get("safehouse_id"))

    s = SafeHouse.query.get(sid)
    if not s:
        return jsonify({"ok": False, "error": "Safehouse not found"}), 404

    s.occupied = 0
    db.session.commit()
    return jsonify({"ok": True, "available": s.capacity})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
