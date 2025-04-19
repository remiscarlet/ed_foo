import argparse
from datetime import datetime, timedelta, timezone
import pprint

from src.ed_types import Coordinates
from src.populated_galaxy_systems import PopulatedGalaxySystems


class StoreSystemNameWithCoords(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        system = PopulatedGalaxySystems.get_system(values)
        coords = Coordinates(0, 0, 0) if system is None else system.coords
        setattr(namespace, "current_coords", coords)
        pprint.pprint(namespace)


def get_time_since(dt: datetime):
    """Returns a string of weeks, days, hours since supplied `dt`
    Eg, timedelta(days=20, hours=5) => "2 Weeks, 6 Days, 5 Hours Ago"
        timedelta(days=1, hours=1) => "1 Week, 1 Hour Ago"
    """
    delta = datetime.now(timezone.utc) - dt

    days = delta.days
    seconds = delta.total_seconds() - (days * 24 * 60 * 60)
    hours = seconds // (60 * 60)
    config = {
        "Week": int(days // 7),
        "Day": int(days % 7),
        "Hour": int(hours),
    }

    parts = []
    for unit, num in config.items():
        if num > 0:
            part = f"{num} {unit}"
            if num > 1:
                part += "s"
            parts.append(part)

    time_since = ", ".join(parts)
    return f"{time_since} Ago"