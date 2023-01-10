from io import BytesIO
import logging
from flask import Flask, Response, request, json, send_file
from enumeration.dem_data_source import DEMDataSource
from enumeration.dem_file_name import DemFileName
from enumeration.mime_type import MimeType
from enumeration.status_code import StatusCode
from gpx.gpx_read import extract_elevation, extract_track_points
from gpx.gpx_write import add_elevation_element, add_track_points, replace_existing_elevations
from service.approximation import  get_approximated_elevations
from service.geo import calculate_lattice_size, clear_points, convert_to_list, generate_square_lattice, get_bounding_box, restore_square_lattice, validate_lattice
from dem.dem_reader import extract_elevations_from_dem
import xml.etree.ElementTree as ET
import sys

app = Flask(__name__)
logger = logging.getLogger(__name__)
MIN_OFFSET = 5
MAX_OFFSET = 15
MIN_POINTS_COUNT = 3
GPX_NAMESPACE = "http://www.topografix.com/GPX/1/1"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route("/elevation-service/linear-route/",  methods=['POST'])
def get_elevation_linear_route():        
        ET.register_namespace('', GPX_NAMESPACE)        
        
        gpx_file = request.files.get('gpx_file')
        
        if gpx_file == None:
                return send_error_response('Gpx file not set', StatusCode.BAD_REQUEST)

        tree = None
        try:
                tree = ET.parse(gpx_file)
        except:
               return send_error_response('Invalid gpx', StatusCode.BAD_REQUEST)

        root = tree.getroot()
        track_points = extract_track_points(root)
        elevations = extract_elevation(root)

        if len(track_points) == 0:
              return send_error_response('Track points are not added', StatusCode.BAD_REQUEST)

        elevations_jaxa =  extract_elevations_from_dem(DemFileName.ALOS_WORLD, track_points)
        elevations_srtm_90_m = extract_elevations_from_dem(DemFileName.SRTM_90_M, track_points)
        elevations_srtm_30_m = extract_elevations_from_dem(DemFileName.SRTM_30_M, track_points)
        elevations_map = { DEMDataSource.SRTM_30_M: elevations_srtm_30_m, DEMDataSource.SRTM_90_M: elevations_srtm_90_m, DEMDataSource.ALOS_WORLD_3D_30_M: elevations_jaxa }
        approximated_elevations = get_approximated_elevations(elevations_map, track_points)
                
        if len(elevations) == 0:
                add_elevation_element(root, approximated_elevations)
        else:
                replace_existing_elevations(root, approximated_elevations)

        gpx_file.seek(0)
        gpx_file.truncate(0)
        tree.write(gpx_file)
        gpx_file.seek(0)
        file_content = gpx_file.read()

        return send_file(BytesIO(file_content), mimetype=MimeType.GPX_XML, as_attachment=True, download_name=gpx_file.filename)

@app.route("/elevation-service/closed-contour-route/",  methods=['POST'])
def get_elevation_closed_contour_route():
        ET.register_namespace('', GPX_NAMESPACE)        

        gpx_file = request.files.get('gpx_file')
        extracted_offset = request.form.get('offset')

        if gpx_file == None and extracted_offset == None:
                return send_error_response('Gpx file and offset are not set', StatusCode.BAD_REQUEST)

        if gpx_file == None:
                return send_error_response('Gpx file not set', StatusCode.BAD_REQUEST)
        
        if extracted_offset == None:
                return send_error_response('Offset not set', StatusCode.BAD_REQUEST)

        if not extracted_offset.isdigit():
                return send_error_response('Offset cannot contain letters or symbols', StatusCode.BAD_REQUEST)

        offset = int(extracted_offset)

        if offset != MIN_OFFSET and offset != MAX_OFFSET:
                offset = MIN_OFFSET

        tree = None
        try:
                tree = ET.parse(gpx_file)
        except:
               return send_error_response('Invalid gpx', StatusCode.BAD_REQUEST)

        root = tree.getroot()
        track_points = extract_track_points(root)
        
        if len(track_points) < MIN_POINTS_COUNT:
              return send_error_response('At least 3 points are required', StatusCode.BAD_REQUEST)

        bounding_box = get_bounding_box(track_points)
        lattice_size = calculate_lattice_size(bounding_box)
        lattice = generate_square_lattice(int(offset), int(lattice_size), bounding_box)
        lattice_as_list = convert_to_list(lattice)
        cleared_points = clear_points(track_points, lattice_as_list)
        restored_lattice = restore_square_lattice(int(offset), int(lattice_size), cleared_points, lattice)
        valid_lattice = validate_lattice(float(int(offset) + 0.5), restored_lattice)

        if valid_lattice == None or len(valid_lattice) == 0:
                return send_error_response("Cannot generate lattice, please try again with another route or offset", StatusCode.UNPROCESSABLE_ENTITY)

        elevations_jaxa =  extract_elevations_from_dem('output_AW3D30.tif', valid_lattice)
        elevations_srtm_90_m = extract_elevations_from_dem('output_SRTMGL3.tif', valid_lattice)
        elevations_srtm_30_m = extract_elevations_from_dem('output_SRTMGL1.tif', valid_lattice)
        elevations_map = { DEMDataSource.SRTM_30_M: elevations_srtm_30_m, DEMDataSource.SRTM_90_M: elevations_srtm_90_m, DEMDataSource.ALOS_WORLD_3D_30_M: elevations_jaxa }
        approximated_elevations = get_approximated_elevations(elevations_map, valid_lattice)
        
        add_track_points(root, approximated_elevations, valid_lattice)

        gpx_file.seek(0)
        gpx_file.truncate(0)
        tree.write(gpx_file)
        gpx_file.seek(0)
        file_content = gpx_file.read()

        return send_file(BytesIO(file_content), mimetype=MimeType.GPX_XML, as_attachment=True, download_name=gpx_file.filename)

def send_error_response(message, status_code):
    body = {"message": message, "status_code": status_code}

    return Response(json.dumps(body), status_code, mimetype=MimeType.JSON)