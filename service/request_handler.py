from io import BytesIO
import xml.etree.ElementTree as ET
from flask import send_file
from dem.dem_reader import extract_elevations_from_dem
from domain.location import Location
from enumeration.dem_data_source import DEMDataSource
#from enumeration.dem_file_name import DemFileName
from enumeration.error_message import ErrorMessage
from enumeration.mime_type import MimeType
from exception.request_error import RequestError
from gpx.gpx_read import extract_elevation, extract_track_points
from gpx.gpx_write import add_elevation_element, add_track_points, replace_existing_elevations
from service.approximation import calculate_approximated_elevations
from service.geo import calculate_lattice_size, clear_points, generate_square_lattice, get_bounding_box, restore_square_lattice, validate_lattice

GPX_NAMESPACE = "http://www.topografix.com/GPX/1/1"

def handle_linear_route_request(received_gpx_file):
    ET.register_namespace('', GPX_NAMESPACE)

    validate_gpx_file(received_gpx_file)

    try:
        tree = ET.parse(received_gpx_file)
    except ET.ParseError:
        raise RequestError(ErrorMessage.INVALID_GPX)

    root = tree.getroot()
    track_points = extract_track_points(root)
    elevations = extract_elevation(root)

    if not track_points:
        raise RequestError(ErrorMessage.TRACK_POINTS_NOT_FOUND)

    approximated_elevations = get_approximated_elevations(track_points)

    if not elevations:
        add_elevation_element(root, approximated_elevations)
    else:
        replace_existing_elevations(root, approximated_elevations)

    received_gpx_file.seek(0)
    received_gpx_file.truncate(0)
    tree.write(received_gpx_file)
    received_gpx_file.seek(0)
    updated_gpx_file_content = received_gpx_file.read()

    return send_file(BytesIO(updated_gpx_file_content), mimetype=MimeType.GPX_XML, as_attachment=True, download_name=received_gpx_file.filename)

def handle_closed_contour_route_request(received_gpx_file, received_offset):
    ET.register_namespace('', GPX_NAMESPACE)        

    validate_closed_contour_parts(received_gpx_file, received_offset)

    try:
        tree = ET.parse(received_gpx_file)
    except ET.ParseError:
        raise RequestError(ErrorMessage.INVALID_GPX)

    root = tree.getroot()
    track_points = extract_track_points(root)

    if len(track_points) < 3:
        raise RequestError(ErrorMessage.MIN_POINTS_REQUIRED)

    offset = get_offset(received_offset)
    square_lattice = handle_square_lattice_generation(track_points, offset)
    approximated_elevations = get_approximated_elevations(square_lattice)

    add_track_points(root, approximated_elevations, square_lattice)

    received_gpx_file.seek(0)
    received_gpx_file.truncate(0)
    tree.write(received_gpx_file)
    received_gpx_file.seek(0)
    updated_gpx_file_content = received_gpx_file.read()

    return send_file(BytesIO(updated_gpx_file_content), mimetype=MimeType.GPX_XML, as_attachment=True, download_name=received_gpx_file.filename)

def handle_square_lattice_generation(track_points, offset):
    bounding_box = get_bounding_box(track_points)
    lattice_size = int(calculate_lattice_size(bounding_box))
    lattice = generate_square_lattice(offset, lattice_size, bounding_box)
    lattice_as_list = [Location(element.lng, element.lat) for row in lattice for element in row]
    cleared_points = clear_points(track_points, lattice_as_list)
    restored_lattice = restore_square_lattice(offset, lattice_size, cleared_points, lattice)

    return validate_lattice(float(offset), restored_lattice)

def get_offset(received_offset):
    min_offset = 5
    max_offset = 15
    offset = int(received_offset)

    if offset != min_offset and offset != max_offset:
        offset = min_offset

    return offset

def get_approximated_elevations(track_points):
    elevations_jaxa = [] #extract_elevations_from_dem(DemFileName.ALOS_WORLD, track_points)
    elevations_srtm_90_m = [] #extract_elevations_from_dem(DemFileName.SRTM_90_M, track_points)
    elevations_srtm_30_m = [] #extract_elevations_from_dem(DemFileName.SRTM_30_M, track_points)
    elevations = {DEMDataSource.SRTM_30_M: elevations_srtm_30_m, DEMDataSource.SRTM_90_M: elevations_srtm_90_m, DEMDataSource.ALOS_WORLD_3D_30_M: elevations_jaxa}

    return calculate_approximated_elevations(elevations, track_points)

def validate_closed_contour_parts(gpx_file, extracted_offset):
    if gpx_file is None and extracted_offset is None:
        raise RequestError(ErrorMessage.GPX_FILE_AND_OFFSET_NOT_SET)

    if extracted_offset is None:
        raise RequestError(ErrorMessage.OFFSET_NOT_SET)

    if not extracted_offset.isdigit():
        raise RequestError(ErrorMessage.INVALID_OFFSET)

    validate_gpx_file(gpx_file)

def validate_gpx_file(gpx_file):
    if gpx_file is None:
        raise RequestError(ErrorMessage.GPX_FILE_NOT_SET)