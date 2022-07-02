from werkzeug.datastructures import FileStorage
import xml.etree.ElementTree as ET

from domain.location import Location

def extract_track_points(file):
       tree = ET.parse(file)
       root = tree.getroot()
       locations = list()

       for element in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
               attributes = element.attrib
               lat = float(attributes['lat'])
               lng = float(attributes['lon'])
               location = Location(lng, lat)
               locations.append(location)
       return locations
