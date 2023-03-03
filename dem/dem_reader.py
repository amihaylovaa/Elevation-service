import logging
from osgeo import gdal

PIXEL_WIDTH_IDX = 1
PIXEL_HEIGHT_IDX = 5
UPPER_LEFT_PIXEL_LON_IDX = 0
UPPER_LEFT_PIXEL_LAT_IDX = 3

def extract_elevations_from_dem(dem_file, track_points):
    logging.info("Read from DEM")

    src_ds = gdal.Open(dem_file,  gdal.GA_ReadOnly)
    gt = src_ds.GetGeoTransform()
    rb = src_ds.GetRasterBand(1)
    pixel_width = gt[PIXEL_WIDTH_IDX] # w - e (pixel width)
    pixel_height = gt[PIXEL_HEIGHT_IDX] # n - s (pixel height)
    upper_left_corner_longitude = gt[UPPER_LEFT_PIXEL_LON_IDX]
    upper_left_corner_latitude = gt[UPPER_LEFT_PIXEL_LAT_IDX]

    elevations = list()
    for point in track_points:
        point_latitude = point.lat
        point_longitude = point.lng
        row_idx = int((point_longitude - upper_left_corner_longitude) / pixel_width)
        column_idx = -int((upper_left_corner_latitude - point_latitude) / pixel_height)
            
        try:
            elevation = rb.ReadAsArray(row_idx, column_idx, 1, 1)

            elevations.append(float(elevation[0][0]))
        except:
            elevations.append(0)

    src_ds = None

    return elevations