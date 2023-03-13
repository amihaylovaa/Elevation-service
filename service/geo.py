import logging
from math import radians, cos, sin, asin, sqrt, atan2, degrees
from shapely.geometry import Point, Polygon
from domain.location import Location
from enumeration.error_message import ErrorMessage
from exception.lattice_generation_error import LatticeGenerationError

SOUTH_WEST_COORDINATES = 'south-west'
NORTH_EAST_COORDINATES = 'north-east'
ONE_DEGREE_LATITUDE_IN_METERS = 111_111.0

def get_bounding_box(track_points):
    logging.info("Bounding box calculation")

    min_lat = 90.0
    min_lng = 180.0
    max_lat = -90.0
    max_lng = -180.0
    bounding_box = {}

    for point in track_points:
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
    bbox_width = abs(max_location.lat - min_location.lat)
    bbox_width_in_meters = ONE_DEGREE_LATITUDE_IN_METERS * bbox_width
    bbox_height_in_meters = sqrt(diagonal ** 2  - bbox_width_in_meters ** 2)

    return bbox_height_in_meters if bbox_height_in_meters > bbox_width_in_meters else bbox_width_in_meters

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
        for _ in range(meter_offset, lattice_size, meter_offset):
            prev_point = next_row[k - 1]
            new_lng = calculate_next_point_longitude(prev_point, meter_offset)
            next_point = Location(new_lng, prev_point.lat)

            next_row.append(next_point)

            k += 1

        square_lattice.append(next_row)

    return square_lattice

def calculate_next_point_longitude(prev_point, meter_offset):
    prev_lat = prev_point.lat
    prev_lng = prev_point.lng

    lng_offset = radians(meter_offset /  (ONE_DEGREE_LATITUDE_IN_METERS * cos(radians(prev_lat))))
    tmp_lng = prev_lng + degrees(lng_offset)
    tmp_next_point = Location(tmp_lng, prev_lat)

    bearing = calculate_bearing(prev_point, tmp_next_point)
    next_point = calculate_next_point(prev_point, meter_offset, bearing)

    return next_point.lng

def clear_points(original_route_points, generated_square_lattice_points):
    logging.info("Clear points which do not lie inside the square lattice")

    polygon = Polygon([[route_point.lng, route_point.lat] for route_point in original_route_points ])
    generated_points = [ Point(point.lng, point.lat) for point in generated_square_lattice_points ]
    final_lattice_points = list()

    for generated_point in generated_points:
        if polygon.intersects(generated_point):
            point = Location(generated_point.x, generated_point.y)
            final_lattice_points.append(point)            

    return final_lattice_points

def restore_square_lattice(meter_offset, size, cleared_points, final_lattice_points):
    logging.info("Restore lattice")

    max_offset = meter_offset + 0.5
    restored_lattice_points = list()
    current_lattice = convert_list_to_square_lattice(meter_offset, size, final_lattice_points, cleared_points)

    for i, current_row in enumerate(current_lattice):
        row = list()

        if validate_has_elements_on_current_row(i, current_lattice):
            break

        for j, current_element in enumerate(current_row):
            if has_start_points_issues(i, j, max_offset, current_element, current_row, current_lattice):
                continue
            if has_end_points_issues(i, j, max_offset, current_element, current_row, current_lattice):
                break
            row.append(current_element)
        restored_lattice_points.append(row)

    return restored_lattice_points

# TODO current_row and current_element can be extracted from current_lattice
def has_start_points_issues(i, j, max_offset, current_element, current_row, current_lattice):
    if i == len(current_lattice) - 1:
        return (j == 0 and j != len(current_row) - 1 and are_start_points_separated(current_element, current_row[j + 1], max_offset) 
            and not should_add_first_point(i, i - 1, j, max_offset, current_lattice))

    return (j == 0 and are_start_points_separated(current_element, current_row[j + 1], max_offset) 
        and not should_add_first_point(i, i + 1, j, max_offset, current_lattice)) or not should_add_point(i, j, max_offset, current_lattice, len(current_row))

def has_end_points_issues(i, j, max_offset, current_element, current_row, current_lattice):
    if i == len(current_lattice) - 1:
        return j == (len(current_row) - 1 
                        and are_last_points_separated(current_element, current_row[j - 2], max_offset)
                            and not should_add_last_point(i, i - 1, j, max_offset, current_lattice))
            
    return (j == len(current_row) - 1
                        and are_last_points_separated(current_element, current_row[j - 2], max_offset)
                            and not should_add_last_point(i, i - 1, j - 1, max_offset, current_lattice))

def convert_list_to_square_lattice(meter_offset, size, final_lattice_points, cleared_points):
    logging.info('List to lattice conversion')

    p = 0
    current_lattice = list()
    for _ in range(meter_offset, size, meter_offset):
        row = list()

        q = 0
        for _ in range(meter_offset, size, meter_offset):
            current_point = final_lattice_points[p][q]

            if (current_point in cleared_points):
                row.append(current_point)
            q += 1

        p += 1
        
        current_lattice.append(row)

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
    except IndexError:
        return True

def should_add_first_point(curr_row_idx, row_idx, col_idx, max_offset, lattice):
    if len(lattice[row_idx]) <= 1:
        return True

    point = lattice[row_idx][col_idx]
    point_to_compare = lattice[curr_row_idx][col_idx]
    distance = find_distance(point.lng, point.lat, point_to_compare.lng, point_to_compare.lat)

    if distance > max_offset:
        return False

    return len(lattice[curr_row_idx]) < len(lattice[row_idx])

def are_start_points_separated(current_point, next_point, max_offset):
    distance_between_points = find_distance(current_point.lng, current_point.lat, next_point.lng, next_point.lat)

    return distance_between_points > max_offset

def are_last_points_separated(current_point, previous_point, max_offset):
    distance_between_points = find_distance(previous_point.lng, previous_point.lat, current_point.lng, current_point.lat)

    return distance_between_points > max_offset

def should_add_last_point(curr_row_idx, prev_row_idx, col_idx, max_offset, lattice):
    prev_point = lattice[prev_row_idx][len(lattice[prev_row_idx]) - 1]
    point_to_compare = lattice[curr_row_idx][col_idx]
    distance = find_distance(prev_point.lng, prev_point.lat, point_to_compare.lng, point_to_compare.lat)

    if distance < max_offset:
        return True

    return len(lattice[curr_row_idx]) < len(lattice[prev_row_idx])

def validate_lattice(offset, lattice):
    max_offset = offset + 0.5
    logging.info("Lattice validation")

    final_points = list()
    for i, current_row in enumerate(lattice):

        if validate_has_elements_on_current_row(i, lattice):
            break

        for j, current_point in enumerate(current_row[:-1]):
            next_point = current_row[j + 1]
            distance_between_points = find_distance(current_point.lng, current_point.lat, next_point.lng, next_point.lat)

            if  distance_between_points <= max_offset:
                final_points.append(current_point)
            else:
                handle_distance_longer_than_max_offset(i, j, lattice, next_point, offset)

        final_points.append(current_row[-1])

    return final_points

def handle_distance_longer_than_max_offset(i, j, lattice, next_point, max_offset):
    if (j == 0 or j == len(lattice) - 2):
        logging.info("The edge points are placed farther than the maximum offset.")

        raise LatticeGenerationError(ErrorMessage.LATTICE_CANNOT_BE_GENERATED)

    if not has_row_breaking(i, j + 2, max_offset, next_point, lattice):
        logging.info("Row breaking.")

        raise LatticeGenerationError(ErrorMessage.LATTICE_CANNOT_BE_GENERATED)

def validate_has_elements_on_current_row(current_idx, lattice):
    is_not_first_or_last_row = (current_idx != 0 and current_idx != len(lattice) - 1)

    if len(lattice[current_idx]) <= 1 and is_not_first_or_last_row and has_insufficient_elements_to_the_end(current_idx, lattice):
        logging.info("Row with one or zero points")

        raise LatticeGenerationError(ErrorMessage.LATTICE_CANNOT_BE_GENERATED)

    return len(lattice[current_idx]) <= 1 and not has_insufficient_elements_to_the_end(current_idx, lattice)

def has_insufficient_elements_to_the_end(current_idx, lattice):
    for idx in range(current_idx, len(lattice)):
        if len(lattice[idx]) >= 1:
            return True
    return False

def has_row_breaking(i, j, max_offset, next_point, lattice):
    for k in range(j, len(lattice[i]), 1):
        after_next_point = lattice[i][k]
        distance = find_distance(next_point.lng, next_point.lat, after_next_point.lng, after_next_point.lat)

        if distance <= max_offset:
            return True

        next_point = after_next_point
    return False