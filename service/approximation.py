import logging

from enumeration.dem_data_source import DEMDataSource

def get_approximated_elevations(dem_results, track_points):
    logging.info("Elevation approximation")

    srtm_30m = dem_results[DEMDataSource.SRTM_30_M]
    srtm_90m = dem_results[DEMDataSource.SRTM_90_M]
    aw_3d_30m = dem_results[DEMDataSource.ALOS_WORLD_3D_30_M]
    elevations = list()

    for i in range(0, len(track_points), 1):
        srtm_30m_elevation = srtm_30m[i]
        srtm_90m_elevation = srtm_90m[i]
        aw_3d_30m_elevation = aw_3d_30m[i]
        
        if abs(srtm_90m_elevation - srtm_30m_elevation) > 2.0 or abs(srtm_90m_elevation - aw_3d_30m_elevation) > 2.0:
            elevations.append((srtm_30m_elevation + aw_3d_30m_elevation) / 2.0)
        else:
            elevations.append((srtm_30m_elevation + srtm_90m_elevation + aw_3d_30m_elevation) / 3.0)
    return elevations