import logging
import xml.etree.ElementTree as ET
from enumeration.gpx_element import GPXElement

ELEVATION_TAG = 'ele'
TRACK_POINT_TAG = 'trkpt'
NEW_LINE = '\n'

def replace_existing_elevations(root, approximated_elevations):
    logging.info("Elevation replacement")

    elevation_elements = root.findall(GPXElement.ELEVATION)

    for idx, element in enumerate(elevation_elements):
        element.text = str(approximated_elevations[idx])

def add_elevation_element(root, approximated_elevations):
    logging.info("Elevation adding")

    track_points = root.findall(GPXElement.TRACK_POINT)

    for idx, track_point in enumerate(track_points):
        ele = ET.SubElement(track_point, ELEVATION_TAG)
        ele.text = str(approximated_elevations[idx])
        ele.tail = NEW_LINE

def add_track_points(root, approximated_elevations, generated_track_points):
    logging.info("Track point adding")

    track_segments = root.findall(GPXElement.TRACK_SEGMENT)
    last_track_segment = track_segments[-1]

    for idx, track_point in enumerate(generated_track_points):
        track_point_element = ET.SubElement(
            last_track_segment, TRACK_POINT_TAG, lat = str(track_point.lat), lon = str(track_point.lng)
        )
        track_point_element.tail = NEW_LINE
        ele = ET.SubElement(track_point_element, ELEVATION_TAG)
        ele.text = str(approximated_elevations[idx])
        ele.tail = NEW_LINE