from geopy import geocoders
from geopy import distance

geolocator = geocoders.Nominatim(user_agent="simple_travel_bot")


def get_distance(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    if None in [latitude1, longitude1]:
        return 0
    if None in [latitude2, longitude2]:
        return 10**9
    return distance.geodesic((latitude1, longitude1), (latitude2, longitude2)).km


def get_coords(address: str) -> tuple:
    if address is None:
        return None, None
    try:
        location = geolocator.geocode(address)
        if location is None:
            return None, None
        return location.latitude, location.longitude
    except Exception:
        return None, None
