from typing import Optional
import httpx

from app.config import get_settings
from app.schemas import DiscoveryFilters, DiscoveryResult, DiscoveredBusiness

settings = get_settings()


# Google Places category -> Google Places type keyword mapping
CATEGORY_KEYWORDS = {
    "Hospitals": "hospital",
    "Clinics": "clinic",
    "Hotels": "hotel",
    "Restaurants": "restaurant",
    "Schools": "school",
    "Colleges": "university",
    "Real estate agencies": "real_estate_agency",
    "Textile companies": "textile",
    "Manufacturers": "factory",
    "Travel agencies": "travel_agency",
    "Construction companies": "construction",
    "Digital agencies": "marketing",
    "Local shops": "store",
}


class GooglePlacesProvider:
    name = "google_places"

    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def _location_bias(self, filters: DiscoveryFilters) -> str:
        parts = []
        if filters.city:
            parts.append(filters.city)
        if filters.state:
            parts.append(filters.state)
        if filters.country:
            parts.append(filters.country)
        return ", ".join(parts) if parts else "Tamil Nadu, India"

    async def discover(self, filters: DiscoveryFilters) -> DiscoveryResult:
        if not self.api_key:
            raise RuntimeError(
                "Google Places API key not configured. Set GOOGLE_PLACES_API_KEY in .env"
            )

        keyword = CATEGORY_KEYWORDS.get(filters.category, filters.category)
        query = f"{keyword} in {self._location_bias(filters)}"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.displayName,places.formattedAddress,places.internationalPhoneNumber,"
                "places.websiteUri,places.id,places.types,places.location"
            ),
        }
        body = {
            "textQuery": query,
            "pageSize": min(filters.limit, 20),
            "languageCode": "en",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(self.base_url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                raise RuntimeError(f"Google Places API request failed: {exc}")
            except ValueError as exc:
                raise RuntimeError(f"Google Places API returned invalid JSON: {exc}")

        places = data.get("places", [])
        businesses = []
        seen = set()
        for p in places:
            name = p.get("displayName", {}).get("text") or "Unnamed business"
            place_id = p.get("id")
            website = p.get("websiteUri")
            phone = p.get("internationalPhoneNumber")
            address = p.get("formattedAddress")

            domain = None
            if website:
                from urllib.parse import urlparse
                domain = urlparse(website).hostname
                if domain and domain.startswith("www."):
                    domain = domain[4:]
            if domain and domain in seen:
                continue
            if domain:
                seen.add(domain)

            city = filters.city
            state = filters.state
            country = filters.country

            businesses.append(DiscoveredBusiness(
                business_name=name,
                category=filters.category,
                city=city,
                state=state,
                country=country,
                website=website,
                phone=phone,
                email=None,
                address=address,
                source_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
                discovery_provider="google_places",
                google_place_id=place_id,
            ))

        coverage_note = (
            "Discovery powered by Google Places API (New). Requires a valid Google Places API key. "
            "Results depend on Google Places data coverage in the selected area. Not all businesses "
            "have websites listed. Results are a sample, not a complete business registry."
        )
        return DiscoveryResult(
            total=len(businesses),
            businesses=businesses[: filters.limit],
            provider=self.name,
            coverage_note=coverage_note,
            filters=filters,
        )


def get_discovery_provider(provider_name: str = "osm"):
    if provider_name == "google_places":
        return GooglePlacesProvider()
    from app.discovery.overpass import OverpassProvider
    return OverpassProvider()
