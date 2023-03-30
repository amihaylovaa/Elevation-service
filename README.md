**Elevation service** is a REST-based web application written in Python and built with Flask 
It provides for track points elevations aggregated from three different Digital Elevation Model (DEM) files and calculated by a simple algorithm.

The application receives a GPX file which describes either a linear route or a closed contour.

## Linear route
For the linear route for each track point in the GPX file elevations are 
aggregated from the DEM files and added to it. If elevation data are already presented in the GPX file, they are replaced by the generated ones from the application.

End point - `/elevation-service/linear-route/`

Request body :

````
{
  "gpx_file": <the-gpx-file>
}
````


## Closed contour
When the route is presented as closed contour a square lattice of track points is generated within the area closed by the contour. 
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

** The square lattice is formed by 7 stepes: **

1) Extracting the track points of the gpx file
2) Defining the bounding box of the contour (represented the route) 
3) Calculating the size of the contour ( width and height of ) of the contour. The greater of both is the size of the square lattice.
4) Square lattice generation
5) Removing points which do not belong to the contour
6) Square lattice restoration
7) Square lattice validation


