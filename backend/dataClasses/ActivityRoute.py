from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import polyline

Coordinate = Tuple[float, float]

@dataclass
class ActivityRoute:
    id: int
    name: str
    polyline: Optional[str]
    coordinates: list[Coordinate]

    def __init__(self, id: int, name: str, polyline: Optional[str], coordinates: list[Coordinate]):
        self.id = id
        self.name = name
        self.polyline = polyline
        self.coordinates = coordinates

    @staticmethod
    def _decode(poly_str: Optional[str]) -> List[Coordinate]:
        if poly_str is None:
            return []
        return polyline.decode(poly_str)

    @classmethod
    def from_api(cls, activity_data: Dict[str, Any]) -> 'ActivityRoute':
        id = activity_data.get("id")
        name = activity_data.get("name")
        map_info = activity_data.get("map", {})
        poly = map_info.get("summary_polyline")
        coords = cls._decode(poly)
        return cls(id=id, name=name, polyline=poly, coordinates=coords)

    @classmethod
    def build_many(cls, activities_data: Iterable[Dict[str, Any]]) -> List['ActivityRoute']:
        return [cls.from_api(activity) for activity in activities_data]