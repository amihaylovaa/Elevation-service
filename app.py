from flask import Flask, Response, request, json
from enumeration.mime_type import MimeType
from enumeration.request_part import RequestPart
from enumeration.status_code import StatusCode
from exception.lattice_generation_error import LatticeGenerationError
from exception.request_error import RequestError
from service.handler import handle_closed_contour_route_request, handle_linear_route_request
import xml.etree.ElementTree as ET
import sys
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@app.route("/elevation-service/linear-route/",  methods=['POST'])
def get_elevation_linear_route():      
    received_gpx_file = request.files.get(RequestPart.GPX_FILE)

    try:
        return handle_linear_route_request(received_gpx_file)
    except RequestError as request_error_message:
        return send_error_response(str(request_error_message), StatusCode.BAD_REQUEST)

@app.route("/elevation-service/closed-contour-route/",  methods=['POST'])
def get_elevation_closed_contour_route():
    received_gpx_file = request.files.get(RequestPart.GPX_FILE)
    received_offset = request.form.get(RequestPart.OFFSET)

    try:
        return handle_closed_contour_route_request(received_gpx_file, received_offset)
    except RequestError as request_error_message:
        return send_error_response(str(request_error_message), StatusCode.BAD_REQUEST)
    except LatticeGenerationError as lattice_generation_error_message:
        return send_error_response(str(lattice_generation_error_message), StatusCode.UNPROCESSABLE_ENTITY)

def send_error_response(message, status_code):
    body = {"message": message}

    return Response(json.dumps(body), status_code, mimetype=MimeType.JSON)