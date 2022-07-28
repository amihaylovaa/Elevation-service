def get_approximated_elevations(dem_results, generated_points):
    srtm_30m = dem_results['srtm30m']
    srtm_90m = dem_results['srtm90m']
    aw_3d_30m = dem_results['aw3d30m']
    elevations = list()

    for i in range(0, len(generated_points), 1):
        srtm_30m_elevation = srtm_30m[i]
        srtm_90m_elevation = srtm_90m[i]
        aw_3d_30m_elevation = aw_3d_30m[i]
        
        if abs(srtm_90m_elevation - srtm_30m_elevation) > 2.0 or abs(srtm_90m_elevation - aw_3d_30m_elevation) > 2.0:
            elevations.append((srtm_30m_elevation + aw_3d_30m_elevation) / 2.0)
        else:
            elevations.append((srtm_30m_elevation + srtm_90m_elevation + aw_3d_30m_elevation) / 3.0)
    return elevations