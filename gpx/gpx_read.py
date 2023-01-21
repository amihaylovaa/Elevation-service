import logging
import xml.etree.ElementTree as ET
from domain.location import Location
from enumeration.gpx_element import GPXElement

LATITUDE_ATTRIBUTE = 'lat'
LONGITUDE_ATTRIBUTE = 'lon'

def extract_track_points(root):
    logging.info("Track point extraction")

    locations = list()

    for element in root.findall(GPXElement.TRACK_POINT):
        attributes = element.attrib
        lat = float(attributes[LATITUDE_ATTRIBUTE])
        lng = float(attributes[LONGITUDE_ATTRIBUTE])
               
        location = Location(lng, lat)
        locations.append(location)
       
    return locations

def extract_elevation(root):
    logging.info("Elevation extraction")

    elevations = list()

    for element in root.findall(GPXElement.ELEVATION):
        elevation = float(element.text)
        elevations.append(elevation)

    return elevations