#////////////////
#  add_land  ///
#//////////////
#---------------------------------------------------------------------
# Add land feature to cartopy figure
#---------------------------------------------------------------------
#/////////////////
#  add_coast  ///
#///////////////
#---------------------------------------------------------------------
# Add coast feature to cartopy figure
#---------------------------------------------------------------------

#////////////////
#  add_land  ///
#//////////////
#---------------------------------------------------------------------
# Add land features to cartopy figure
#---------------------------------------------------------------------
# DEPENDENCIES:
#-------------
import numpy as np
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.colors
from shapely import wkt
#---------------------------------------------------------------------
def add_land(ax, scale = '50m', color='gray', alpha=1, fill_dateline_gap = True, zorder=2):
    
    """Add land feature to cartopy figure
    
INPUT:
- ax: cartopy figure axis
- scale = NaturalEarthFeature land feature scale (e.g. '10m', '50m', '110m')
        (default: '50m')
- color = land color (e.g. 'k' or [0.9,0.6,0.5]) (default: 'gray')
- alpha = land opacity (default: 1)
- zorder: drawing order of land layer (default: 2)
- fill_dateline_gap: specify whether to fill gap in cartopy land feature along 
   dateline that crosses Russia and Wrangel Island (default: True)

OUTPUT:
- input plot with added land layer

DEPENDENCIES:
import numpy as np
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib as mpl
from matplotlib import pyplot as plt
from shapely import wkt

Latest recorded update:
05-11-2022

    """
    
        
    # grab land from cfeat.NaturalEarthFeature
    #-----------------------------------------
    ax.add_feature(cfeat.NaturalEarthFeature(category='physical', name='land', 
                                             scale=scale, facecolor=color),
                                             alpha = alpha, zorder = zorder)

    # if specified, fill dateline gap in land feature with shapely polygons
    if fill_dateline_gap == True:
        # generate polygon to fill line across Wrangel Island and line across Russia
        WKT_fill_Wrangel = 'POLYGON ((-180.1 71.51,-180.1 71.01,-179.9 71.01,-179.9 71.51,-180.1 71.51))'
        poly1 = wkt.loads(WKT_fill_Wrangel)
        ax.add_geometries([poly1], crs=ccrs.PlateCarree(), 
              facecolor=color, edgecolor=color, alpha = alpha, zorder=zorder)
        WKT_fill_Russia = 'POLYGON ((-180.1 65.1,-180.1 68.96,-179.9 68.96,-179.9 65.1,-180.1 65.1))'
        poly2 = wkt.loads(WKT_fill_Russia)
        ax.add_geometries([poly2], crs=ccrs.PlateCarree(), 
              facecolor=color, edgecolor=color, alpha = alpha, zorder=zorder)


        
#/////////////////
#  add_coast  ///
#///////////////
#---------------------------------------------------------------------
# Add coast feature to cartopy figure
#---------------------------------------------------------------------
# DEPENDENCIES:
import numpy as np
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.colors
#---------------------------------------------------------------------
def add_coast(ax, scale = '50m', color='gray', linewidth = 1, alpha=1, zorder=3):

    """Add land feature to cartopy figure
    
INPUT:
- ax: cartopy figure axis
- scale = NaturalEarthFeature coast feature scale (e.g. '10m', '50m', '110m')
        (default: '50m')
- color = coastline color (e.g. 'k' or [0.9,0.6,0.5]) (default: 'gray')
- linewidth = coastline linewidth (default: 1)
- alpha = coastline opacity (default: 1)
- zorder: drawing order of coast layer (default: 3)

OUTPUT:
- input plot with added coast layer

DEPENDENCIES:
import numpy as np
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib as mpl
from matplotlib import pyplot as plt
from shapely import wkt

Latest recorded update:
05-06-2022

    """

    # coastline
    #----------
    ax.coastlines(scale, color=color, linewidth=linewidth, alpha = alpha, zorder = zorder)
