from werkzeug.datastructures import FileStorage
import xml.etree.ElementTree as ET

from domain.location import Location

def extract_track_points(root):
       locations = list()

       for element in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
               attributes = element.attrib
               lat = float(attributes['lat'])
               lng = float(attributes['lon'])
               location = Location(lng, lat)
               locations.append(location)
       return locations


def extract_elevation(root):
       elevations = list()

       for element in root.findall('.//{http://www.topografix.com/GPX/1/1}ele'):
                elevation = float(element.text)
                print(elevation)
                elevations.append(elevation)
       return elevations