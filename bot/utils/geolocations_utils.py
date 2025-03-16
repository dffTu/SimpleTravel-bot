import geopy

geolocator = geopy.geocoders.Nominatim(user_agent="simple_travel_bot")


def get_distance(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    if None in [latitude1, longitude1, latitude2, longitude2]:
        return 10**9
    return geopy.distance.geodesic((latitude1, longitude1), (latitude2, longitude2)).km


def get_coords(address: str) -> tuple:
    try:
        location = geolocator.geocode(address)
        if location is None:
            return None, None
        return location.latitude, location.longitude
    except Exception:
        return None, None
