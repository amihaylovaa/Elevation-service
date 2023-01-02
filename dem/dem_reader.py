import logging
from osgeo import gdal

def extract_elevations_from_dem(dem_file, points):
        logging.info("Read from DEM")

        src_ds = gdal.Open(dem_file,  gdal.GA_ReadOnly)
        gt = src_ds.GetGeoTransform()
        rb = src_ds.GetRasterBand(1)
        pixel_width = gt[1] # w - e (pixel width)
        pixel_height = gt[5] # n - s (pixel height)
        upper_left_corner_longitude = gt[0]
        upper_left_corner_latitude = gt[3]
        elevations = list()
        
        for p in points:
                point_latitude = p.lat
                point_longitude = p.lng
                row = int((point_longitude - upper_left_corner_longitude) / pixel_width)
                column = -int((upper_left_corner_latitude - point_latitude) / pixel_height)
                try:
                 elevation = rb.ReadAsArray(row, column, 1, 1)
                 elevations.append(int(elevation[0][0]))
                except:
                 elevations.append(0)


        src_ds = None

        return elevations