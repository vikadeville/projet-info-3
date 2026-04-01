from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import requests
import math

app = Flask(__name__)
app.config["SECRET_KEY"] = "projet_velo"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialisation login manager et base
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy()
db.init_app(app)

# -------------------------
# MODELE UTILISATEUR
# -------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    preferedcity = db.Column(db.String(250), nullable=True)
    lastitinerary = db.Column(db.String(250), nullable=True)


# Création des tables si elles n'existent pas
with app.app_context():
    db.create_all()


# Nécessaire pour Flask-Login
@login_manager.user_loader
def loader_user(user_id):
    return db.session.get(User, int(user_id))


# -------------------------
# PAGE PRINCIPALE
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------
# INSCRIPTION
# -------------------------
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return redirect(url_for("index"))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user is not None:
        return redirect(url_for("index"))

    new_user = User(
        username=username,
        password=password,
        preferedcity="",
        lastitinerary=""
    )
    
    db.session.add(new_user)
    db.session.commit()

    # Connexion automatique après création du compte
    login_user(new_user)

    return redirect(url_for("index"))


# -------------------------
# CONNEXION
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    user = User.query.filter_by(username=username).first()

    if user is not None and user.password == password:
        login_user(user)

    return redirect(url_for("index"))


# -------------------------
# DECONNEXION
# -------------------------
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# -------------------------
# SAUVEGARDE DU PROFIL
# -------------------------
@app.route("/saveProfile", methods=["POST"])
def save_profile():
    if not current_user.is_authenticated:
        return jsonify({"error": "Utilisateur non connecté"}), 401

    data = request.get_json(silent=True) or {}

    city = data.get("preferedcity")
    itinerary = data.get("lastitinerary")

    user = db.session.get(User, current_user.id)
    if user is None:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    if city is not None:
        user.preferedcity = city

    if itinerary is not None:
        # On limite la taille pour rester cohérent avec String(250)
        user.lastitinerary = str(itinerary)[:250]

    db.session.commit()

    return jsonify({
        "success": True,
        "username": user.username,
        "preferedcity": user.preferedcity,
        "lastitinerary": user.lastitinerary
    })


# -------------------------
# PROFIL UTILISATEUR COURANT
# -------------------------
@app.route("/getProfile", methods=["GET"])
def get_profile():
    if not current_user.is_authenticated:
        return jsonify({
            "authenticated": False
        })

    user = db.session.get(User, current_user.id)

    return jsonify({
        "authenticated": True,
        "username": user.username,
        "preferedcity": user.preferedcity,
        "lastitinerary": user.lastitinerary
    })


# -------------------------
# API STATIONS PROCHES
# -------------------------
API_KEY = "f2898848aea2a84165d3dd04e96c8e9c78e6f7bd"

@app.route("/getBikesAround", methods=["GET"])
def get_bikes():
    user_lat = request.args.get("lat")
    user_lng = request.args.get("lng")
    ville = request.args.get("ville", "lyon")
    type_station = request.args.get("type", "depart")

    if not user_lat or not user_lng:
        return jsonify({"error": "Coordonnées manquantes"}), 400

    try:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
    except ValueError:
        return jsonify({"error": "Coordonnées invalides"}), 400

    url = "https://api.jcdecaux.com/vls/v1/stations"
    params = {"contract": ville, "apiKey": API_KEY}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Erreur API JCDecaux"}), 500

    stations = response.json()
    resultat = []

    for s in stations:
        if s["status"] != "OPEN":
            continue

        if type_station == "depart" and s["available_bikes"] <= 0:
            continue

        if type_station == "arrivee" and s["available_bike_stands"] <= 0:
            continue

        lat = s["position"]["lat"]
        lng = s["position"]["lng"]
        distance = math.sqrt((lat - user_lat) ** 2 + (lng - user_lng) ** 2)

        resultat.append({
            "name": s["name"],
            "lat": lat,
            "lng": lng,
            "velos": s["available_bikes"],
            "places": s["available_bike_stands"],
            "distance": distance
        })

    resultat.sort(key=lambda x: x["distance"])
    return jsonify(resultat[:3])

# -------------------------
# API TRAJET
# -------------------------
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFjODhjOTJiZTljZDQ3Njg5NjA2YzIwYjViZDVjNjM3IiwiaCI6Im11cm11cjY0In0="

@app.route("/getTrajectory", methods=["GET"])
def get_trajectory():
    start_lat = request.args.get("start_lat")
    start_lng = request.args.get("start_lng")
    end_lat = request.args.get("end_lat")
    end_lng = request.args.get("end_lng")
    mode = request.args.get("mode", "foot-walking")

    if not all([start_lat, start_lng, end_lat, end_lng]):
        return jsonify({"error": "Coordonnées manquantes"}), 400

    try:
        start_lat = float(start_lat)
        start_lng = float(start_lng)
        end_lat = float(end_lat)
        end_lng = float(end_lng)
    except ValueError:
        return jsonify({"error": "Coordonnées invalides"}), 400

    url = f"https://api.openrouteservice.org/v2/directions/{mode}"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [
            [start_lng, start_lat],
            [end_lng, end_lat]
        ],
        "instructions": False
    }

    resp = requests.post(url, json=body, headers=headers)

    if resp.status_code != 200:
        return jsonify({"error": "Erreur ORS"}), 500

    return jsonify(resp.json())


# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)