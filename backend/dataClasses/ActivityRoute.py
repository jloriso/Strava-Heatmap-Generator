from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import polyline

Coordinate = Tuple[float, float]

@dataclass
class ActivityRoute:
    id: int
    name: str
    start_date: str
    time_zone: str
    activity_type: str
    distance: float
    moving_time: int
    elasped_time: int
    polyline: Optional[str]
    coordinates: list[Coordinate]

    def __init__(self, id: int, name: str, start_date: str, time_zone: str, activity_type: str, distance: float, moving_time: int, elapsed_time: int, polyline: Optional[str], coordinates: list[Coordinate]):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.time_zone = time_zone
        self.activity_type = activity_type
        self.distance = distance
        self.moving_time = moving_time
        self.elapsed_time = elapsed_time
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
        start_date = activity_data.get("start_date")
        time_zone = activity_data.get("timezone")
        activity_type = activity_data.get("type")
        distance = activity_data.get("distance")
        moving_time = activity_data.get("moving_time")
        elapsed_time = activity_data.get("elapsed_time")
        map_info = activity_data.get("map", {})
        poly = map_info.get("summary_polyline")
        coords = cls._decode(poly)
        return cls(id=id, name=name, start_date=start_date, time_zone=time_zone, activity_type=activity_type, distance=distance, moving_time=moving_time, elapsed_time=elapsed_time, polyline=poly, coordinates=coords)

    @classmethod
    def from_db(cls, activity_data: Dict[str, Any]) -> 'ActivityRoute':
            id = activity_data.get("id")
            name = activity_data.get("name")
            start_date = activity_data.get("start_date")
            time_zone = activity_data.get("time_zone")
            activity_type = activity_data.get("activity_type")
            distance = activity_data.get("distance")
            moving_time = activity_data.get("moving_time")
            elapsed_time = activity_data.get("elapsed_time")
            poly = activity_data.get("polyline")
            coords = cls._decode(poly)
            return cls(id=id, name=name, start_date=start_date, time_zone=time_zone, activity_type=activity_type, distance=distance, moving_time=moving_time, elapsed_time=elapsed_time, polyline=poly, coordinates=coords)

    @classmethod
    def build_many_from_api(cls, activities_data: Iterable[Dict[str, Any]]) -> List['ActivityRoute']:
        return [cls.from_api(activity) for activity in activities_data]

    @classmethod
    def build_many_from_db(cls, activities_data: Iterable[Dict[str, Any]]) -> List['ActivityRoute']:
        return [cls.from_db(activity) for activity in activities_data]