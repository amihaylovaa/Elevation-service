from math import radians, cos, sin, asin, sqrt, atan2, degrees, pi
from shapely.geometry import Point, Polygon
from domain.location import Location

def get_bounding_box(route):
    min_lat = 180.0
    min_lng = 180.0
    max_lat = 0.0
    max_lng = 0.0
    boundingBox = {}
    
    for point in route:
        lat = point.lat
        lng = point.lng

        if min_lat > lat:
            min_lat = lat
            
        if min_lng > lng:
            min_lng = lng

        if max_lat < lat: 
            max_lat = lat
            
        if max_lng < lng:
            max_lng = lng

    boundingBox['south-west'] = Location(min_lng, min_lat)
    boundingBox['north-east'] = Location(max_lng, max_lat)

    return boundingBox
    
def get_lattice_size(bounding_box):
    min_location = bounding_box["south-west"]
    max_location = bounding_box["north-east"]
    bounding_box_width = max_location.lat - min_location.lat   
    diagonal = find_distance(min_location.lng, min_location.lat, max_location.lng, max_location.lat)
    bounding_box_width_in_meters = 111_319.44 * bounding_box_width # // circumfirence / 360 // 15.584
    bounding_box_height_in_meters = sqrt(diagonal * diagonal - bounding_box_width_in_meters * bounding_box_width_in_meters)

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
    next_point_lng = radians(next_point.lng)
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
    
def generate_points(meter_offset, size, route, bounding_box):
    square = list()
    min_location = bounding_box['south-west']

    for i in range(meter_offset, size, meter_offset):
        row = list()
        lat_offset = radians(i / 111_319.44)
        new_lat = min_location.lat + degrees(lat_offset)
        start_point = Location(min_location.lng, new_lat)

        row.append(start_point)

        k = 1
        for j in range(meter_offset, size, meter_offset):
            prev_lat = row[k - 1].lat
            prev_lng = row[k - 1].lng
            lng_offset = radians(meter_offset /  (111_318.44 * cos(radians(prev_lat))))
            tmp_location = Location((prev_lng + degrees(lng_offset)), prev_lat)
            bearing = calculate_bearing(row[k - 1], tmp_location)
            new_lng = move_point(row[k - 1], meter_offset, radians(bearing)).lng
            new_point = Location(new_lng, prev_lat)
            row.append(new_point)
            k+=1
    
        square.append(row)
    return square

def move_point(location, range, bearing):
    lat = radians(location.lat)
    lng = radians(location.lng)
    angular_distance = range / 6_371_000.00

    new_lat = asin(sin(lat) * cos(angular_distance) + cos(lat) * sin(angular_distance) * bearing)
    d_lng = atan2(sin(bearing) * sin(angular_distance) * cos(lat), cos(angular_distance) - sin(lat) * sin(lat) )

    new_lng = ((lng + d_lng + pi) % (pi * 2)) - pi

    return Location(degrees(new_lng), degrees(new_lat))

def convert_to_list(generated_points):
    points_list = list()

    for i in range(len(generated_points)):
        for j in range(len(generated_points[i])):
            point = Location(generated_points[i][j].lng, generated_points[i][j].lat)
            points_list.append(point)            
    return points_list

def clear_points(route, generated):
        original_polygon = Polygon([[p.lng, p.lat] for p in route ])

        final_points=[]
        generated_points = list()

        for p in generated:
                lat = p.lat
                lng = p.lng
                point = Point(lng, lat)
                generated_points.append(point)

        for p in generated_points:
                 if original_polygon.intersects(p):
                        # print("%f %f" % (p.y, p.x))
                        point = {"lat": p.y, "lng": p.x}
                        location = Location(p.x, p.y)
                        final_points.append(location)

        return final_points

# def generate_final_points(meter_offset, size, cleared_points, square):
#     max_size = 0
#     final_points = list()

#     p = 0
#     for i in range(meter_offset, size, meter_offset):

#         row = list()
#         missing_points_count = 0
#         q = 0
        
#         for j in range(meter_offset, size, meter_offset):
#             point = square[p][q]

#             if point in cleared_points:
#                 row.append(point)
#             else:
#                 missing_points_count+=1

#             q+=1
    
#         final_points.append(row)
    
#         if missing_points_count > max_size:
#             max_size = missing_points_count
#         p+=1
    
#     lattice = list()

#     for i in range(max_size):
#         for j in range(len(final_points[i])):
#             if len(final_points[i]) % 2 != 0 and j == len(final_points[i]) - 1:
#                      break
#             if j == len(final_points[i]) - 1:
#                 prev_point = final_points[i][j-1]
#                 curr_point = final_points[i][j]
#                 dist = find_distance(prev_point.lng, prev_point.lat, curr_point.lng, curr_point.lat)
#                 if dist > 5: 
#                     if (len(lattice) % 2 != 0):
#                         pass
#                     break
#             final_point = final_points[i][j]
#             lattice.append(final_point)
#     return lattice   


def generate_final_points(meter_offset, size, cleared_points, square):
    max_size = 0
    final_points = list()
    lattice = list()
    p = 0

    for i in range(meter_offset, size, meter_offset):
        row = list()
        q = 0
        for j in range(meter_offset, size, meter_offset):
            current_point = square[p][q]

            if (current_point in cleared_points):
                row.append(current_point)
            q+=1
        p+=1
        lattice.append(row)
        
    for i in range(0, len(lattice), 1):
        if i != (len(lattice) - 1):
            if len(lattice[i]) != len(lattice[i + 1]) and len(lattice[i]) < len(lattice[i + 1]):
                len_diff = len(lattice[i + 1]) - len(lattice[i])
                if len_diff % 2 != 0:
                    for j in range(0, len(lattice[i]) - 1, 1):
                        if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 1]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if(distance > 5):
                                break
                        final_points.append(lattice[i][j])
                else:
                    for j in range(0, len(lattice[i]), 1):
                        if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 1]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if(distance > 5):
                                break
                        final_points.append(lattice[i][j])
            else:
                for j in range(0, len(lattice[i]), 1):
                    if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 1]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if(distance > 5):
                                break
                    final_points.append(lattice[i][j])
        else:
            if len(lattice[i]) != len(lattice[i - 1]) and len(lattice[i]) < len(lattice[i - 1]):
                len_diff = len(lattice[i - 1]) - len(lattice[i])
                if len_diff % 2 != 0:
                   for j in range(0, len(lattice[i]) - 1, 1):
                        if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 1]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if distance > 5:
                                break
                        final_points.append(lattice[i][j])
                else:
                    for j in range(0, len(lattice[i]), 1):
                        if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 1]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if(distance > 5):
                                break
                        final_points.append(lattice[i][j])
            else:
                for j in range(0, len(lattice[i]), 1):
                        if (j == len(lattice) - 1):
                            prev_point = lattice[i][j - 2]
                            distance = find_distance(prev_point.lng, prev_point.lat, lattice[i][j].lng, lattice[i][j].lat)
                            if distance > 5:
                                break
                        final_points.append(lattice[i][j])

    return final_points