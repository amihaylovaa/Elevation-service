**Elevation service** is a REST-based web application written in Python and build with Flask which provides elevations aggregated 
from three different Digital Elevation Model (DEM) files and calculated by a simple algorithm.

The application receives a GPX file which describes either a linear route or a closed contour.

## Linear route
When the route is linear for each track point in the GPX file elevation data are 
aggregated from the DEM files and added to it.

End point - `/elevation-service/linear-route/`

Request body :

````
{
  "gpx_file": <the-gpx-file>
}
````


## Closed contour
When the route is closed contour a square lattice of track points is generated within the area closed by the contour. 
Then elevations for the generated points are aggregated and both the points and the corresponding elevations are included in the GPX file.
Besides the gpx file an offset must be included in the request - 5m or 15m, which determines the distance between each point of the square lattice.

End point - `/elevation-service/closed-contour-route/`

Request body :

````
{
  "gpx_file": <the-gpx-file>,
  "offset": <5 or 15>
}
````


