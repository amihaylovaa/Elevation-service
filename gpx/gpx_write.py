from werkzeug.datastructures import FileStorage
import xml.etree.ElementTree as ET

from domain.location import Location

def replace_existing_elevations(root, approximated_elevations):
    idx = 0
    elevation_elements = root.findall('.//{http://www.topografix.com/GPX/1/1}ele')
    for element in elevation_elements:
        element.text = str(approximated_elevations[idx])
        idx = idx + 1

def add_elevation_element(root, approximated_elevations):
    idx = 0
    track_points = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
    for track_point in track_points:
        ele = ET.SubElement(track_point, "ele")
        ele.text = approximated_elevations[idx]
        idx = idx + 1

