# PointBarrowLead_Extraction

Routine for extracting sea ice lead coordinates at 5 km geodesic steps from Level1B thermal infrared MODIS imagery.

## [Lead_Extraction.ipynb](https://github.com/mackenziejewell/PointBarrowLead_Extraction/blob/main/Lead_Extraction.ipynb)

The notebook **Lead_Extraction.ipynb** shows an example routine to extract lead coordinates from a composite image of the Beaufort and Chukchi Seas ice cover on February 20, 2013 from Level1B thermal infrared (band 31) Terra/MODIS imagery files (https://doi.org/10.5067/MODIS/MOD021KM.061, https://doi.org/10.5067/MODIS/MOD03.061). For this example, files were downloaded from the [NASA LAADS DAAC](https://ladsweb.modaps.eosdis.nasa.gov/) and stored locally. All that is needed to run this example routine are the MODIS imagery files listed in `MODIS_file_list.txt` and the python packages used in the notebook.

<img src="https://github.com/mackenziejewell/PointBarrowLeadFormation/blob/main/example.gif" width=60% height=60%>

---

There are three main sections of the notebook.

### (1) Plotting imagery around Point Barrow
Open hdf files of L1B thermal infrared MODIS imagery and save to a projected image in grayscale.

### (2) Extracting lead coordinates from projected image
Use interactive figure window to manually select some lead coordinates with [mpl_point_clicker](https://mpl-point-clicker.readthedocs.io/en/latest/index.html#) and use [sci-kit image active contour model](https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.active_contour) to fill in additional coordinates between selected points based on the brightness contrast across leads in thermal images.

### (3) Re-indexing lead coordinates to 5-km geodesic steps
Use [geopy](https://geopy.readthedocs.io/en/stable/) and [metpy](https://unidata.github.io/MetPy/latest/index.html#) to re-index/interpolate lead coordinates to fall along 5-km geodesic steps. 

Additional instructions provided directly in the notebook.
