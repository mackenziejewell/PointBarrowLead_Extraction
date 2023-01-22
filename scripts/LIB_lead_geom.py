#///////////////////////
#  make_SpacedArray ///
#/////////////////////
#----------------------------------------------------------------------------
# make_SpacedArray input array of lead coordinates spaces evenly geodetically
#----------------------------------------------------------------------------
# DEPENDENCIES:
#-------------
# DEPENDENCIES:
import numpy as np
from matplotlib import pyplot as plt
#pip install geopy
from geopy.distance import geodesic
# pip install metpy
import metpy
from metpy import interpolate
from pyproj import CRS
#---------------------------------------------------------------------

def make_SpacedArray(lead, step_km = 10, error_km = 1, PROJ = CRS.from_epsg(4326), show_plot = False):
    
    """Evenly space array of lead coordinates (geodetically)
    
INPUT:
- lead: array of lead coordinates (Nx2 with [Lat, Lon])
- step_km: desired geodesic step size, arc distance between coordinates (km) (default: 10)
- error_km: max allowed error size on step (km) (default: 1), error will usually be l/2 max
- PROJ: PyProj Coordinate Reference System to use for the output
- show_plot: bool, whether to display plot (default: False)

OUTPUT:
- LatArray (re-spaced lead latitudes)
- LonArray (re-spaced lead longitudes, 0-360)

DEPENDENCIES:
import numpy as np
from matplotlib import pyplot as plt
from geopy.distance import geodesic
import metpy
from metpy import interpolate
from pyproj import CRS

Latest recorded update:
01-22-2023

    """
    
    
    # create empty arrays to fill with desired coordinates
    LatArray = np.array([lead[0,0]])
    if lead[0,1] < 0:
        LonArray = np.array([lead[0,1]+360])
    else:
        LonArray = np.array([lead[0,1]])
        
        
    # index for moving along lead coordinates
    ii=0

    while ii < lead.shape[0]:    
        # break the loop once it reaches end of the lead
        # (break if the distance between given point and last point is less than step)
        if geodesic((lead[ii,0],lead[ii,1]), (lead[-1,0],lead[-1,1])).km <= step_km:
            break

        # begin to loop through all points(jj) after point(ii)
        for jj in range(ii,lead.shape[0]):
            # calculate distance between point(ii) and point(jj)
            ds = geodesic((lead[ii,0],lead[ii,1]), (lead[jj,0],lead[jj,1])).km
            # if ds (point(ii) - point(jj)) exceeds chosen step size
            if ds > step_km:

                # break geodesic between ii and jj into NumSteps, specified above
                NumSteps=round(ds/error_km)
                # calculate index of waypoint nearest to specified step size
                NewIndex = round(step_km/error_km)
                # create geodesic line and extract coordinate closest to step
                NewLoc = metpy.interpolate.geodesic(PROJ, (lead[ii,0],lead[ii,1]), (lead[jj,0],lead[jj,1]), NumSteps+1)[NewIndex]
                # convert to only positive longitude values
                if NewLoc[0]<0:
                    NewLoc[0] = NewLoc[0]+360
                # add new coordinate to list
                LatArray = np.append(LatArray, NewLoc[1])
                LonArray = np.append(LonArray, NewLoc[0])

                break

        # update new location in array as starting point for next iteration        
        lead[jj,0] =  NewLoc[1]
        lead[jj,1] =  NewLoc[0]
        # iterate again, starting from point(jj)
        ii = jj
    
    # create array for arcdistance between coordinates
    dsarray = np.array([])
    for ii in range(0, LatArray.shape[0]-1):
        ds = geodesic((LatArray[ii],LonArray[ii]),(LatArray[ii+1],LonArray[ii+1])).km
        dsarray = np.append(dsarray, ds)

    if show_plot == True:
        plt.plot(range(0,len(dsarray)), dsarray)
        plt.ylabel('Arcdistance')
        plt.xlabel('Site Index')
        plt.ylim(np.mean(dsarray)-2*error_km,np.mean(dsarray)+2*error_km)
    
    return LatArray, LonArray