const map = L.map("map").setView([CITY.lat, CITY.lng], CITY.zoom);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap"
}).addTo(map);

const markersLayer = L.layerGroup().addTo(map);

// Appel API maison dès le chargement
fetch(`/getBikesAround?lat=${CITY.lat}&lng=${CITY.lng}&radius=1200&contract=${CITY.contract}`)
  .then(res => res.json())
  .then(data => {
    console.log("JSON /getBikesAround =", data);

    markersLayer.clearLayers();
    (data.stations || []).forEach(s => {
      const popup = `
        <b>${s.name || "Station"}</b><br/>
        ${s.address || ""}<br/>
        Vélos: ${s.available_bikes} — Places: ${s.available_bike_stands}<br/>
        Statut: ${s.status}<br/>
        Distance: ${s.distance_m} m
      `;
      L.marker([s.lat, s.lng]).addTo(markersLayer).bindPopup(popup);
    });
  })
  .catch(err => {
    console.error("Erreur fetch /getBikesAround", err);
  });