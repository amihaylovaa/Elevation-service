import logging
from enumeration.dem_data_source import DEMDataSource

MAX_DIFFERENCE = 2.0

def calculate_approximated_elevations(elevations, track_points):
    logging.info("Elevation approximation")

    srtm_30m = elevations[DEMDataSource.SRTM_30_M]
    srtm_90m = elevations[DEMDataSource.SRTM_90_M]
    aw_3d_30m = elevations[DEMDataSource.ALOS_WORLD_3D_30_M]
    elevations = list()

    for i in range(0, len(track_points), 1):
        srtm_30m_elevation = srtm_30m[i]
        srtm_90m_elevation = srtm_90m[i]
        aw_3d_30m_elevation = aw_3d_30m[i]
        
        elevation = None
        if (abs(srtm_90m_elevation - srtm_30m_elevation) > MAX_DIFFERENCE 
                or abs(srtm_90m_elevation - aw_3d_30m_elevation) > MAX_DIFFERENCE):
            elevation = (srtm_30m_elevation + aw_3d_30m_elevation) / 2
        else:
            elevation = (srtm_30m_elevation + srtm_90m_elevation + aw_3d_30m_elevation) / 3
        
        elevations.append(elevation)

    return elevations