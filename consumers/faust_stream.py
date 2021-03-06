"""Defines trends calculations for stations"""
import logging
from dataclasses import dataclass

import faust


logger = logging.getLogger(__name__)


@dataclass
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


@dataclass
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str



app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")

stations_topic = app.topic("cta.connect.stations", value_type=Station)

out_topic = app.topic("cta.stations.transformed", partitions=1)

stations_transformed_table = app.Table(
   "stations-transformed-table",
   default=list,
   partitions=1,
   changelog_topic=out_topic,
)

@app.agent(stations_topic)
async def stations(stations):
    async for station in stations:
        stations_transformed_table['station_id'] = {
            'station_id': station.station_id,
            'station_name': station.station_name,
            'order': station.order,
            'line': get_color(station)
        }

def get_color(station):
    if station.red:
        return 'red'
    if station.blue:
        return 'blue'
    if station.green:
        return 'green'


if __name__ == "__main__":
    app.main()
