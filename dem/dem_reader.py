from osgeo import gdal

def read_dem_file(dem, points):
        src_ds = gdal.Open(dem,  gdal.GA_ReadOnly)
        gt = src_ds.GetGeoTransform()
        rb = src_ds.GetRasterBand(1)
        pixel_resolution_to_pixel_width = gt[1] # w - e (pixel width)
        pixel_resolution_to_pixel_height = gt[5] # n - s (pixel height)
        upper_left_corner_longitude = gt[0]
        upper_left_corner_latitude = gt[3]
        elevations = list()

        for p in points:
                point_latitude = p.lat
                point_longitude = p.lng
                row = int((point_longitude - upper_left_corner_longitude) / pixel_resolution_to_pixel_width)
                column = -int((upper_left_corner_latitude - point_latitude) / pixel_resolution_to_pixel_height)
                elevation = rb.ReadAsArray(row, column, 1, 1)
                elevations.append(int(elevation[0][0]))

        src_ds = None

        return elevations