from src.ingestion.spansh.models.station_spansh import StationSpansh
from src.postgresql.postgresql.db import StationsDB


def test_validate_station_cache_keys_match() -> None:
    owner_id = 12345
    station = {"id": 54321, "owner_id": owner_id, "name": "foobar's landing", "distance_to_arrival": 1234.56}
    station_spansh = StationSpansh.model_validate(station)
    station_obj = StationsDB(**station)
    assert station_spansh.to_cache_key(owner_id) == station_obj.to_cache_key()
