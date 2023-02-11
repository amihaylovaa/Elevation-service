import logging
from math import radians, cos, sin, asin, sqrt, atan2, degrees
from shapely.geometry import Point, Polygon
from domain.location import Location

SOUTH_WEST_COORDINATES = 'south-west'
NORTH_EAST_COORDINATES = 'north-east'
ONE_DEGREE_LATITUDE_IN_METERS = 111_111.0

def get_bounding_box(route):
    logging.info("Bounding box calculation")

    min_lat = -90.0
    min_lng = -180.0
    max_lat = 90.0
    max_lng = 180.0
    bounding_box = {}

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

    bounding_box[SOUTH_WEST_COORDINATES] = Location(min_lng, min_lat)
    bounding_box[NORTH_EAST_COORDINATES] = Location(max_lng, max_lat)

    return bounding_box

def calculate_lattice_size(bounding_box):
    logging.info("Lattice size's calculation")

    min_location = bounding_box[SOUTH_WEST_COORDINATES]
    max_location = bounding_box[NORTH_EAST_COORDINATES]
    diagonal = find_distance(min_location.lng, min_location.lat, max_location.lng, max_location.lat)
    bounding_box_width = abs(max_location.lat - min_location.lat)
    bounding_box_width_in_meters = ONE_DEGREE_LATITUDE_IN_METERS  * bounding_box_width
    bounding_box_height_in_meters = sqrt(diagonal ** 2  - bounding_box_width_in_meters ** 2)

    return bounding_box_height_in_meters if bounding_box_height_in_meters > bounding_box_width_in_meters else bounding_box_width_in_meters

def find_distance(prev_point_lng, prev_point_lat, current_point_lng, current_point_lat):
    latitude_difference = radians(abs(current_point_lat - prev_point_lat))
    longitude_difference = radians(abs(current_point_lng - prev_point_lng))
    x = sin(latitude_difference / 2.0) * sin(latitude_difference / 2.0) + cos(
        radians(prev_point_lat)) * cos(radians(current_point_lat)) * sin(longitude_difference / 2.0) * sin(
            longitude_difference / 2.0)
    
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

def calculate_next_point(prev_point, offset, bearing):
    r = 6371.00 * 1000.00
    angular_distance = offset / r
    prev_point_lat = radians(prev_point.lat)
    prev_point_lng = radians(prev_point.lng)

    next_point_lat = asin(sin(prev_point_lat) * cos(angular_distance)
                + cos(prev_point_lat) * sin(angular_distance) * cos(bearing))

    next_point_lng = prev_point_lng + atan2(sin(bearing) * sin(angular_distance) * cos(prev_point_lat),
                cos(angular_distance) - sin(prev_point_lat) * sin(next_point_lat))

    return Location(degrees(next_point_lng), degrees(next_point_lat))

def generate_square_lattice(meter_offset, lattice_size, bounding_box):
    logging.info("Lattice generation")

    square_lattice = list()
    min_location = bounding_box[SOUTH_WEST_COORDINATES]

    for i in range(meter_offset, lattice_size, meter_offset):
        next_row = list()

        lat_offset = radians(i / ONE_DEGREE_LATITUDE_IN_METERS)
        new_lat = min_location.lat + degrees(lat_offset)
        next_row_start_point = Location(min_location.lng, new_lat)

        next_row.append(next_row_start_point)

        k = 1
        for j in range(meter_offset, lattice_size, meter_offset):
            prev_point = next_row[k - 1]
            prev_lat = prev_point.lat
            prev_lng = prev_point.lng
            
            lng_offset = radians(meter_offset /  (ONE_DEGREE_LATITUDE_IN_METERS * cos(radians(prev_lat))))
            tmp_lng = prev_lng + degrees(lng_offset)
            tmp_next_point = Location(tmp_lng, prev_lat)
            
            bearing = calculate_bearing(prev_point, tmp_next_point)
            new_lng = calculate_next_point(prev_point, meter_offset, bearing).lng
            next_point = Location(new_lng, prev_lat)
            
            next_row.append(next_point)

            k += 1
    
        square_lattice.append(next_row)

    return square_lattice

def convert_to_list(square_lattice):
    points_list = list()

    for i in range(len(square_lattice)):
        for j in range(len(square_lattice[i])):
            point = Location(square_lattice[i][j].lng, square_lattice[i][j].lat)
            
            points_list.append(point)

    return points_list

def create_list_of_points(generated_square_lattice_points):
    generated_points = list()

    for p in generated_square_lattice_points:
        point = Point(p.lng, p.lat)

        generated_points.append(point)
    
    return generated_points

def clear_points(original_route_points, generated_square_lattice_points):
        logging.info("Clear points")

        polygon = Polygon([[route_point.lng, route_point.lat] for route_point in original_route_points ])
        generated_points = create_list_of_points(generated_square_lattice_points)

        final_lattice_points = list()
        for generated_point in generated_points:
            if polygon.intersects(generated_point):
                lattice_point = Location(generated_point.x, generated_point.y)
                final_lattice_points.append(lattice_point)

        return final_lattice_points

def restore_square_lattice(meter_offset, size, cleared_points, final_lattice_points):
    logging.info("Restore lattice")

    max_offset = meter_offset + 0.5
    restored_lattice_points = list()
    current_lattice = convert_list_to_square_lattice(meter_offset, size, final_lattice_points, cleared_points, current_lattice)
   
    for i in range(0, len(current_lattice), 1):
        row = list()

        if i == len(current_lattice) - 1:
                for j in range(0, len(current_lattice[i]), 1):
                    current_element = current_lattice[i][j]

                    if (j == 0 and are_first_elements_separated(current_element, current_lattice[i][j + 1], max_offset) 
                            and not should_add_first_element(i, i - 1, j, max_offset, current_lattice)):
                        continue
                    if (j == len(current_lattice[i]) - 1 
                        and are_last_elements_separated(current_element, current_lattice[i][j - 2], max_offset)
                            and not should_add_last_element(i, i - 1, j, max_offset, current_lattice)):
                        break
                    row.append(current_element)
        else:
                for j in range(0, len(current_lattice[i]), 1):
                    if ((j == 0 and are_first_elements_separated(current_element, current_lattice[i][j + 1], max_offset) 
                            and not should_add_first_element(i, i + 1, j, max_offset, current_lattice))
                        or not should_add_point(i, j, max_offset, current_lattice, len(current_lattice[i]))):
                        continue
                    if (j == len(current_lattice[i]) - 1
                        and are_last_elements_separated(current_element, current_lattice[i][j - 2], max_offset)
                            and not should_add_last_element(i, i - 1, j - 1, max_offset, current_lattice)):
                        break
                    row.append(current_element)

        restored_lattice_points.append(row)

    return restored_lattice_points

def convert_list_to_square_lattice(meter_offset, size, final_lattice_points, cleared_points, current_lattice):
    p = 0
    for i in range(meter_offset, size, meter_offset):
        row = list()

        q = 0
        for j in range(meter_offset, size, meter_offset):
            current_point = final_lattice_points[p][q]

            if (current_point in cleared_points):
                row.append(current_point)
            q += 1

        p += 1
        if (len(row) > 1):
            current_lattice.append(row)
        else:
            return None
    
    return current_lattice

def should_add_point(row_idx, col_idx, max_offset, lattice, lat_size):
    current_point = lattice[row_idx][col_idx]

    try:
        if col_idx == 0 or col_idx == lat_size:
            upper_point = lattice[row_idx - 1][col_idx]
            down_point = lattice[row_idx + 1][col_idx]
            upper_distance = find_distance(current_point.lng, current_point.lat, upper_point.lng, upper_point.lat)
            down_distance = find_distance(current_point.lng, current_point.lat, down_point.lng, down_point.lat)

            return upper_distance < max_offset and down_distance < max_offset
        else:
            return True
    except:
        return True

def should_add_first_element(curr_row_idx, row_idx, col_idx, max_offset, lattice):
    point = lattice[row_idx][col_idx]
    point_to_compare = lattice[curr_row_idx][col_idx]
    distance = find_distance(point.lng, point.lat, point_to_compare.lng, point_to_compare.lat)
    
    if distance > max_offset:
        return False

    return len(lattice[curr_row_idx]) < len(lattice[row_idx])

def are_first_elements_separated(current_point, next_point, max_offset):
    distance_between_points = find_distance(current_point.lng, current_point.lat, next_point.lng, next_point.lat)

    return distance_between_points > max_offset

def are_last_elements_separated(current_point, previous_point, max_offset):
    distance_between_points = find_distance(previous_point.lng, previous_point.lat, current_point.lng, current_point.lat)
    
    return distance_between_points > max_offset

def should_add_last_element(curr_row_idx, prev_row_idx, col_idx, max_offset, lattice):
    prev_point = lattice[prev_row_idx][len(lattice[prev_row_idx]) - 1]
    point_to_compare = lattice[curr_row_idx][col_idx]
    distance = find_distance(prev_point.lng, prev_point.lat, point_to_compare.lng, point_to_compare.lat)
    
    if distance < max_offset:
        return True

    return len(lattice[curr_row_idx]) < len(lattice[prev_row_idx])

def validate_lattice(max_offset, lattice):
    logging.info("Lattice validation")

    final_points = list()

    for i in range(0, len(lattice), 1):
        if len(lattice[i]) <= 1:
            if i == 0 or i == len(lattice) - 1:
                continue
            else:
               logging.error("Row with one or zero points")

               return None

        for j in range(0, len(lattice[i]) - 1, 1):
            current_point = lattice[i][j]
            next_point = lattice[i][j + 1]
            distance_between_points = find_distance(current_point.lng, current_point.lat, next_point.lng, next_point.lat)
            
            if  distance_between_points <= max_offset:
                final_points.append(current_point)
            else:
                if j == 0 or j == len(lattice) - 2:
                    logging.error("The edge points are placed farther than the maximum offset.")

                    return None
                else:
                    try:
                        # TODO - extract to a method where to check not only for after the next point
                        pointCanBeAdded = False
                        for p in range(j + 2, len(lattice[i]), 1):
                            after_next_point = lattice[i][p]
                            distance = find_distance(next_point.lng, next_point.lat, after_next_point.lng, after_next_point.lat)
                    
                            if distance <= max_offset:
                                final_points.append(current_point)

                                pointCanBeAdded = True
                                break

                            next_point = after_next_point
                        if not pointCanBeAdded:
                            logging.error("Two sequential points are placed farther than the maximum offset")

                            return None
                    except:
                        logging.error("Lattice's points are placed farther than the maximum offset")
                        
                        return None

        final_points.append(lattice[i][len(lattice[i]) - 1])

    return final_points