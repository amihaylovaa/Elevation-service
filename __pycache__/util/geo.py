from model.location import Location
from math import radians, cos, sin, asin, sqrt, abs, atan2, degrees

def getBoundingBox(route):
    min_lat = 0.0
    min_lng = 0.0
    max_lat = 90.0
    max_lng = 180.0
    boundingBox = {}
    
    for point in route:
        lat = point.lat
        lng = point.lng

        if min_lat > lat:
            minLat = lat
            
        if min_lng > lng:
            min_lng = lng

        if max_lat < lat: 
            maxLat = lat
            
        if max_lng < lng:
            maxLng = lng

    boundingBox["south-west"] = Location(min_lng, min_lat)
    boundingBox["north-east"] = Location(min_lng, min_lat)

    return boundingBox
    
def get_lattice_size(original_route, bounding_box):
    min_location = bounding_box["south-west"]
    max_location = bounding_box["north-east"]
    bounding_box_width = max_location.lat - min_location.lat     
    diagonal = find_distance(min_location.lng, min_location.lat, max_location.lng, max_location.lat)
    bounding_box_width_in_meters = 111_319.44 * bounding_box_width # // circumfirence / 360 // 15.584
    bounding_box_height_in_meters = sqrt(diagonal ** 2 - bounding_box_width_in_meters ** 2)

    return bounding_box_height_in_meters if bounding_box_height_in_meters > bounding_box_width_in_meters else bounding_box_width_in_meters


def find_distance(prev_point_lng, prev_point_lat, current_point_lng, current_point_lat):
    latitude_difference = radians(abs(current_point_lat - prev_point_lat))
    longitude_difference = radians(abs(current_point_lng - prev_point_lng))
    x = sin(latitude_difference / 2.0) * sin(latitude_difference / 2.0) + cos(radians(prev_point_lat)) * cos(radians(current_point_lat)) * sin(longitude_difference / 2.0) * sin(longitude_difference / 2.0)
    
    dist = 2 * atan2(sqrt(x), sqrt(1 - x))

    return 6_371_000.00 * dist

def calculate_bearing(prev_point, next_point):
    prev_point_lat = radians(prev_point.lat)
    prev_point_lng = radians(prev_point.lng)
    next_point_lat = radians(next_point.lat)
    next_point_lng = radians(next_point_lng.lng)
    dl = next_point_lng - prev_point_lng
    x = cos(prev_point_lat) * sin(next_point_lat) - (sin(prev_point_lat) * cos(next_point_lat) * cos(dl))
    y = cos(prev_point_lat) * sin(dl)

    bearing = degrees(atan2(y, x))

    return (bearing + 360.00) % 360.00


def calculate_next_point(prev_point, bearing):
    r = 6371.00 * 1000.00
    angular_distance = 1.00 / r
    prev_point_lat = radians(prev_point.lat)
    prev_point_lng = radians(prev_point.lng)

    next_point_lat = asin(sin(prev_point_lat) * cos(angular_distance)
                + cos(prev_point_lat) * sin(angular_distance) * cos(bearing))

    next_point_lng = prev_point_lng + atan2(sin(bearing) * sin(angular_distance) * cos(prev_point_lat),
                cos(angular_distance) - sin(prev_point_lat) * sin(next_point_lat))

    return Location(degrees(next_point_lng), degrees(next_point_lat))
    