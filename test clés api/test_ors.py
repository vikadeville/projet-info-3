import requests
import json

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjVmNjYzNDg3ZGM5ZDQ3ZmZhYWY0ZGZmYzlhNTYxNDAwIiwiaCI6Im11cm11cjY0In0="

url = "https://api.openrouteservice.org/v2/directions/cycling-regular/geojson"
headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}

# Coordonnées au format [lon, lat]
body = {
    "coordinates": [
        [2.2945, 48.8584],  # Tour Eiffel
        [2.3376, 48.8606],  # Louvre
    ]
}

r = requests.post(url, headers=headers, json=body, timeout=20)
print("HTTP status:", r.status_code)

try:
    data = r.json()
    summary = data["features"][0]["properties"].get("summary", {})
    print("Distance (m):", summary.get("distance"))
    print("Durée (s):", summary.get("duration"))

    with open("ors_route.geojson", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("OK -> ors_route.geojson généré")
except Exception as e:
    print("Réponse non-JSON ou erreur:", e)
    print("Texte brut (début):", r.text[:300])