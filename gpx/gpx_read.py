import logging
from domain.location import Location
from enumeration.gpx_element import GPXElement

LATITUDE_ATTRIBUTE = 'lat'
LONGITUDE_ATTRIBUTE = 'lon'

def extract_track_points(root):
    logging.info("Track point extraction")

    track_point_elements = root.findall(GPXElement.TRACK_POINT)
    track_points = list()

    for element in track_point_elements:
        attributes = element.attrib
        lat = float(attributes[LATITUDE_ATTRIBUTE])
        lng = float(attributes[LONGITUDE_ATTRIBUTE])               
        track_point = Location(lng, lat)

        track_points.append(track_point)
       
    return track_points

def extract_elevation(root):
    logging.info("Elevation extraction")

    elevation_elements = root.findall(GPXElement.ELEVATION)
    elevations = [float(element.text) for element in elevation_elements]

    return elevations