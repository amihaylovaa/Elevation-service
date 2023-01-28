import logging
import xml.etree.ElementTree as ET
from enumeration.gpx_element import GPXElement

ELEVATION_TAG = 'ele'
TRACK_POINT_TAG = 'trkpt'
NEW_LINE = '\n'

def replace_existing_elevations(root, approximated_elevations):
    logging.info("Elevation replacement")

    idx = 0
    elevation_elements = root.findall(GPXElement.ELEVATION)
    for element in elevation_elements:
        element.text = str(approximated_elevations[idx])
        idx = idx + 1

def add_elevation_element(root, approximated_elevations):
    logging.info("Elevation adding")

    idx = 0
    track_points = root.findall(GPXElement.ELEVATION)
    for track_point in track_points:
        ele = ET.SubElement(track_point, ELEVATION_TAG)
        ele.text = str(approximated_elevations[idx])
        ele.tail = NEW_LINE
        idx = idx + 1

def add_track_points(root, approximated_elevations, generated_track_points):
    logging.info("Track point adding")

    idx = 0
    track_segments = root.findall(GPXElement.TRACK_SEGMENT)
    last_track_segments = track_segments[len(track_segments) - 1]
    
    for track_point in generated_track_points:
        track_point_element = ET.SubElement(
            last_track_segments, TRACK_POINT_TAG, lat = str(track_point.lat), lon = str(track_point.lng)
        )
        track_point_element.tail = NEW_LINE
        ele = ET.SubElement(track_point_element, ELEVATION_TAG)
        ele.text = str(approximated_elevations[idx])
        ele.tail = NEW_LINE

        idx = idx + 1