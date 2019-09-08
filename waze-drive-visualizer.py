#!/usr/bin/env python3

import json
import pprint
from geopy import distance
from datetime import datetime
import plotly.graph_objects as go
import itertools

line_number = 117
path = "./waze-data-archive/account_activity_3.csv"

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

with open(path) as fd:
    for i, line in enumerate(fd, 1):
        if i == line_number:
            raw_drive = line
            break

class Drive(object):
    def __init__(self):
        self.points = []
        self.segments = []

    def plot(self, fig):
        for s in self.segments:
            s.plot(fig)

    def __str__(self):
        return " => ".join([str(s) for s in self.segments])

    @staticmethod
    def from_string(raw):
        drive = Drive()
        for x in raw.split("=>"):
            drive.points.append(
                Point.from_string(x.strip())
            )
        for a, b in pairwise(drive.points):
            drive.segments.append(
                Segment(a, b)
            )
        return drive
            

class Segment(object):
    def __init__(self, from_p, to_p):
        self.from_p = from_p
        self.to_p = to_p

    def get_distance(self):
        return distance.distance(
            (self.from_p.latitude, self.from_p.longitude),
            (self.to_p.latitude, self.to_p.longitude)
        ).km

    def get_duration(self):
        tdelta = self.to_p.timestamp - self.from_p.timestamp
        seconds = tdelta.total_seconds()
        return seconds / (60.0 * 60.0)

    def get_speed(self):
        return self.get_distance() / self.get_duration()
    
    def __str__(self):
        return "{:.0f}km/h".format(
            self.get_speed()
        )

    def plot(self, fig):
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [self.from_p.longitude, self.to_p.longitude],
                lat = [self.from_p.latitude, self.to_p.latitude],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
                hoverinfo = 'text',
                text = "{:.0f}km/h".format(self.get_speed())
            )
        )

class Point(object):
    def __init__(self, latitude, longitude, timestamp):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
    
    @staticmethod
    def from_string(raw):
        ts_raw = raw.split("(")[0]
        ts = datetime.strptime(
            ts_raw,
            "%Y-%m-%d %H:%M:%S"
        )
        pos = raw.split("(")[1][:-1]
        lat, log = [float(x.strip()) for x in pos.split(",")]
        return Point(lat, log, ts)
    
    def __str__(self):
        return "{} ({}, {})".format(
            self.timestamp,
            self.latitude,
            self.longitude
        )

drives = json.loads(raw_drive.replace(";", ","))
for d in drives:
    assert len(d) == 1
    fig = go.Figure()
    drive = Drive.from_string(next(iter(d.values())))
    drive.plot(fig)
    fig.show()

