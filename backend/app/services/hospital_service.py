import requests
import math


def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return round(R * c, 2)


def find_nearby_hospitals(latitude: str, longitude: str, radius_meters: int = 5000, limit: int = 5) -> list:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return []

    query = f"""
    [out:json][timeout:20];
    (
      node["amenity"="hospital"](around:{radius_meters},{lat},{lon});
      way["amenity"="hospital"](around:{radius_meters},{lat},{lon});
    );
    out center;
    """

    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]

    headers = {
        "User-Agent": "ClinicalTriageAgent/1.0 (student project; contact: doctor2@test.com)"
    }

    data = None
    for url in overpass_urls:
        try:
            response = requests.post(url, data={"data": query}, headers=headers, timeout=25)
            response.raise_for_status()
            data = response.json()
            break
        except (requests.RequestException, ValueError) as e:
            continue

    if data is None:
        return []

    
    hospitals = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        h_lat = element.get("lat") or element.get("center", {}).get("lat")
        h_lon = element.get("lon") or element.get("center", {}).get("lon")
        if h_lat is None or h_lon is None:
            continue

        distance = calculate_distance_km(lat, lon, h_lat, h_lon)

        hospitals.append({
            "name": name,
            "latitude": h_lat,
            "longitude": h_lon,
            "distance_km": distance,
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "address": tags.get("addr:full") or tags.get("addr:street", ""),
            "directions_url": f"https://www.google.com/maps/dir/?api=1&destination={h_lat},{h_lon}"
        })

    hospitals.sort(key=lambda h: h["distance_km"])
    return hospitals[:limit]