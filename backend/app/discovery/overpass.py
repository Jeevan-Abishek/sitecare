from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.config import get_settings
from app.schemas import DiscoveryFilters, DiscoveryResult, DiscoveredBusiness
from app.security import validate_url

settings = get_settings()


class BaseDiscoveryProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def discover(self, filters: DiscoveryFilters) -> DiscoveryResult:
        raise NotImplementedError


class OverpassProvider(BaseDiscoveryProvider):
    name = "openstreetmap_overpass"

    # Category -> Overpass tag filter (osm tag key: value regex)
    CATEGORY_TAGS = {
        "Hospitals": 'node["amenity"~"hospital|clinic|doctors"]({{bbox}}); way["amenity"~"hospital|clinic|doctors"]({{bbox}});',
        "Clinics": 'node["amenity"~"clinic|doctors"]({{bbox}}); way["amenity"~"clinic|doctors"]({{bbox}});',
        "Hotels": 'node["tourism"~"hotel|motel|guest_house|hostel"]({{bbox}}); way["tourism"~"hotel|motel|guest_house|hostel"]({{bbox}});',
        "Restaurants": 'node["amenity"~"restaurant|fast_food|cafe|bar"]({{bbox}}); way["amenity"~"restaurant|fast_food|cafe|bar"]({{bbox}});',
        "Schools": 'node["amenity"~"school|kindergarten|college|university"]({{bbox}}); way["amenity"~"school|kindergarten|college|university"]({{bbox}});',
        "Colleges": 'node["amenity"~"college|university"]({{bbox}}); way["amenity"~"college|university"]({{bbox}});',
        "Real estate agencies": 'node["office"="estate_agent"]({{bbox}}); way["office"="estate_agent"]({{bbox}}); node["shop"="estate_agent"]({{bbox}}); way["shop"="estate_agent"]({{bbox}});',
        "Textile companies": 'node["shop"~"fabric|textile|clothes"]({{bbox}}); way["shop"~"fabric|textile|clothes"]({{bbox}});',
        "Manufacturers": 'node["man_made"~"works|factory"]({{bbox}}); way["man_made"~"works|factory"]({{bbox}});',
        "Travel agencies": 'node["office"="tourism"]({{bbox}}); way["office"="tourism"]({{bbox}}); node["shop"="travel_agency"]({{bbox}}); way["shop"="travel_agency"]({{bbox}});',
        "Construction companies": 'node["office"~"construction|architect"]({{bbox}}); way["office"~"construction|architect"]({{bbox}});',
        "Digital agencies": 'node["office"~"it|telecommunication|advertising"]({{bbox}}); way["office"~"it|telecommunication|advertising"]({{bbox}});',
        "Local shops": 'node["shop"]({{bbox}}); way["shop"]({{bbox}});',
    }

    # Bounding boxes [south, west, north, east]
    DEFAULT_BBOXES = {
        ("India", "Tamil Nadu", None): [8.0, 76.2, 13.6, 80.3],
        ("India", "Tamil Nadu", "Chennai"): [12.8, 80.0, 13.2, 80.3],
        ("India", "Tamil Nadu", "Coimbatore"): [10.9, 76.9, 11.1, 77.1],
        ("India", "Tamil Nadu", "Madurai"): [9.8, 78.0, 10.0, 78.2],
    }

    def __init__(self):
        self.api_url = settings.OVERPASS_API_URL
        self.timeout = settings.OVERPASS_TIMEOUT

    def _bbox_for(self, filters: DiscoveryFilters):
        key = (filters.country, filters.state, filters.city)
        if key in self.DEFAULT_BBOXES:
            return self.DEFAULT_BBOXES[key]
        # Fallback: Tamil Nadu bbox
        return self.DEFAULT_BBOXES[("India", "Tamil Nadu", None)]

    def _query_for_category(self, category: str, bbox) -> str:
        if category == "All businesses":
            tags = []
            for cat_filter in self.CATEGORY_TAGS.values():
                tags.append(cat_filter.replace("{{bbox}}", self._bbox_str(bbox)))
            return "(" + "\n".join(tags) + ");"
        tmpl = self.CATEGORY_TAGS.get(category)
        if not tmpl:
            return ""
        return tmpl.replace("{{bbox}}", self._bbox_str(bbox))

    @staticmethod
    def _bbox_str(bbox) -> str:
        return f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

    def _build_overpassql(self, filters: DiscoveryFilters) -> str:
        bbox = self._bbox_for(filters)
        query = self._query_for_category(filters.category, bbox)
        if not query:
            query = self._query_for_category("All businesses", bbox)
        return f"""
[out:json][timeout:{self.timeout}];
({query});
out center tags;
"""

    async def discover(self, filters: DiscoveryFilters) -> DiscoveryResult:
        query = self._build_overpassql(filters)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(self.api_url, data={"data": query})
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                raise RuntimeError(f"Overpass API request failed: {exc}")
            except ValueError as exc:
                raise RuntimeError(f"Overpass API returned invalid JSON: {exc}")

        elements = data.get("elements", [])
        businesses = []
        seen_domains = set()
        for el in elements:
            tags = el.get("tags", {}) or {}
            name = tags.get("name") or tags.get("name:en") or "Unnamed business"
            if not name:
                continue
            website = tags.get("website") or tags.get("website:en")
            if filters.website_available and not website:
                continue
            domain = None
            if website:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(website if "://" in website else "https://" + website).hostname
                    if domain and domain.startswith("www."):
                        domain = domain[4:]
                except Exception:
                    domain = None
            if domain and domain in seen_domains:
                continue
            if domain:
                seen_domains.add(domain)
            addr_parts = []
            for k in ("addr:housenumber", "addr:street", "addr:city", "addr:state", "addr:postcode"):
                v = tags.get(k)
                if v:
                    addr_parts.append(v)
            address = ", ".join(addr_parts) or None
            phone = tags.get("phone") or tags.get("contact:phone")
            email = tags.get("email") or tags.get("contact:email")
            osm_id = el.get("id")
            el_type = el.get("type", "node")
            source_url = f"https://www.openstreetmap.org/{el_type}/{osm_id}" if osm_id else None
            businesses.append(DiscoveredBusiness(
                business_name=name,
                category=filters.category,
                city=tags.get("addr:city") or filters.city,
                state=tags.get("addr:state") or filters.state,
                country=tags.get("addr:country") or filters.country,
                website=website,
                phone=phone,
                email=email,
                address=address,
                source_url=source_url,
            ))

        coverage_note = (
            "Discovery powered by OpenStreetMap Overpass API. Coverage depends on OSM data "
            "in the selected area. Not all businesses have websites or are mapped in OSM; "
            "results are a sample, not a complete business registry."
        )
        return DiscoveryResult(
            total=len(businesses),
            businesses=businesses[: filters.limit],
            provider=self.name,
            coverage_note=coverage_note,
            filters=filters,
        )


def get_discovery_provider() -> BaseDiscoveryProvider:
    return OverpassProvider()
