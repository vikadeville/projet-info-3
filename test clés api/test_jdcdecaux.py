import requests
import json

JCDECAUX_API_KEY = "3d2e8aaf44ce38e5f62b5bda2274b349d885a201"

CONTRACT = "toulouse"

url = "https://api.jcdecaux.com/vls/v1/stations"
params = {"contract": CONTRACT, "apiKey": JCDECAUX_API_KEY}

r = requests.get(url, params=params, timeout=20)
print("HTTP status:", r.status_code)

# Affiche un aperçu du JSON
try:
    data = r.json()
    print("Nb stations:", len(data))
    print("Exemple station (extrait):")
    print({k: data[0].get(k) for k in ["name", "address", "position", "status", "available_bikes", "available_bike_stands"]})

    # Sauvegarde le JSON complet (preuve)
    with open("jcdecaux_stations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("OK -> jcdecaux_stations.json généré")
except Exception as e:
    print("Réponse non-JSON ou erreur:", e)
    print("Texte brut (début):", r.text[:300])