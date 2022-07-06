from util.geo import find_distance

def approximate(dem_results, generated_points):
    srtm_30m = dem_results['srtm30m']
    srtm_90m = dem_results['srtm90m']
    aw_3d_30m = dem_results['aw3d30m']
    elevations = list()

    for i in len(generated_points):
        point = generated_points[i]
        srtm_30m_elevation = srtm_30m[i]
        srtm_90m_elevation = srtm_90m[i]
        aw_3d_30m_elevation = aw_3d_30m[i]
        
        if abs(srtm_90m_elevation - srtm_30m_elevation) > 1.0 or abs(srtm_90m_elevation - aw_3d_30m_elevation) > 1.0:

                if (i > 0):
                    prev_point_lat = generated_points[i - 1].lat
                    prev_point_lng = generated_points[i - 1].lng

                    distance = find_distance(prev_point_lng, prev_point_lat, point.lng, point.lat)
                    curr_elevation = (srtm_30m_elevation + aw_3d_30m_elevation) / 2.0
                    diff = abs(elevations.get(i - 1) - curr_elevation)

                    if (distance <= 15.00 and diff > 1.0):
                        elevations.append(elevations.get(i - 1))
                    else:
                        elevations.append((srtm_30m_elevation + aw_3d_30m_elevation) / 2.0)
                else:
                    elevations.append((srtm_30m_elevation + aw_3d_30m_elevation) / 2.0)
        else:
            elevations.append((srtm_30m_elevation + srtm_90m_elevation + aw_3d_30m_elevation) / 3.0)
            