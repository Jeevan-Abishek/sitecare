from app.discovery.overpass import OverpassProvider, get_discovery_provider as get_overpass_provider
from app.discovery.google_places import GooglePlacesProvider

__all__ = ["OverpassProvider", "GooglePlacesProvider", "get_discovery_provider"]


def get_discovery_provider(provider_name: str = "osm"):
    if provider_name == "google_places":
        return GooglePlacesProvider()
    return get_overpass_provider()
