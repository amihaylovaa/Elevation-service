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
        ele.text = str(approximated_elevations[idx])
        idx = idx + 1

def replace_existing_track_points(root, generated_track_points, approximated_elevations):
    idx = 0
    track_points = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
    for track in track_points:
       root.remove(track)
    
    idx = 0
    generated_elements = list()
    track_segments = root.findall('.//{http://www.topografix.com/GPX/1/1}trkseg')
    for track_segment in track_segments:
        for track_point in generated_track_points:
            if idx == 0:
                track_point_element = ET.SubElement(track_segment, "trkpt", lat = str(track_point.lat), lon = str(track_point.lng))
                ele = ET.SubElement(track_point_element, "ele")
                ele.text = str(approximated_elevations[idx])
                generated_elements.append(track_point_element)
            else:
                track_point_element = ET.SubElement(generated_elements[len(generated_elements) - 1], "trkpt", lat = str(track_point.lat), lon = str(track_point.lng))
                ele = ET.SubElement(track_point_element, "ele")
                ele.text = str(approximated_elevations[idx])
            idx = idx + 1