#////////////////////
#  get_hdf_data  ///
#//////////////////
#---------------------------------------------------------------------
# Load data from hdf file (can load single attribute or full dataset). 
#---------------------------------------------------------------------
#///////////////////////
#  load_MODISband   ///
#/////////////////////
#---------------------------------------------------------------------
# Load a band from MODIS imagery.
#---------------------------------------------------------------------
#////////////////////
#  get_MODISgeo  ///
#//////////////////
#---------------------------------------------------------------------
# Load lat, lon arrays from MODIS geo (hdf) files.
#---------------------------------------------------------------------
#/////////////////////
#  get_MODISdate  ///
#///////////////////
#---------------------------------------------------------------------
# Grab date from MODIS filename, create datetime object.
#---------------------------------------------------------------------
#////////////////////////
#  pair_images_meta  ///
#//////////////////////
#---------------------------------------------------------------------
# Load metadata of MODIS image files from folder.
#---------------------------------------------------------------------


#////////////////////
#  get_hdf_data  ///
#//////////////////
#---------------------------------------------------------------------
# Load data from hdf file (can load single attribute or full dataset). 
#---------------------------------------------------------------------
# DEPENDENCIES
from pyhdf.SD import SD, SDC
#---------------------------------------------------------------------
def get_hdf_data(file,dataset,attr):
    
    """Load data from hdf file (can load single attribute or full dataset).
    
INPUT:
- file: hdf filename with directory  
        (e.g. '/Users/kenzie/MOD021KM.A2000066.2255.061.2017171220013.hdf')
- dataset: desired data set within HDF file 
           (e.g. 'EV_250_Aggr1km_RefSB')
- attr: None OR desired attribute within dataset 
        (e.g. None, 'reflectance_scales')

OUTPUT:
- specified dataset or attribute

DEPENDENCIES:
from pyhdf.SD import SD, SDC

Latest recorded update:
06-03-2022

    """
    
    f = SD(file,SDC.READ)
    data = f.select(dataset)
    # if no attribute, grab full data
    if attr == None:            
        data_or_attr = data[:]
    # or grab attribute from full data
    else:                       
        index = data.attr(attr).index()
        data_or_attr = data.attr(index).get()
    f.end()
    
    return data_or_attr



#///////////////////////
#  load_MODISband   ///
#/////////////////////
#---------------------------------------------------------------------
# Load a band from MODIS imagery.
#---------------------------------------------------------------------
# DEPENDENCIES
import numpy as np
# homemade: get_hdf_data
#---------------------------------------------------------------------

def load_MODISband(file, dataset, band, refrad):

    """Load a band from MODIS imagery. Applies scale factor and offsets,
    makes mask for invalid/missing data values.
    
INPUT:
- file: filename with directory 
        (e.g. '/Users/kenzie/MOD021KM.A2000066.2255.061.2017171220013.hdf')
- dataset: desired data set within HDF file 
           (e.g. 'EV_250_Aggr1km_RefSB')
- band: band number formatted as string 
        (e.g. '30')
- refrad: reflectance or radiance datatype
          ('reflectance' or 'radiance')

OUTPUT:
- band_data: ref or rad band data, "bad" data masked

DEPENDENCIES:
import numpy as np
# homemade: get_hdf_data

Latest recorded update:
06-03-2022

    """
    
    # import data
    #---------------------------------------------------------------------
    band_names = get_hdf_data(file, dataset, 'band_names')
    band_data = get_hdf_data(file, dataset, None)[band_names.split(",").index(band), :, :].astype(np.double)
    if refrad == 'reflectance':
        scales = get_hdf_data(file, dataset, 'reflectance_scales')[band_names.split(",").index(band)]
        offsets = get_hdf_data(file, dataset, 'reflectance_offsets')[band_names.split(",").index(band)]
    elif refrad == 'radiance':
        scales = get_hdf_data(file, dataset, 'radiance_scales')[band_names.split(",").index(band)]
        offsets = get_hdf_data(file, dataset, 'radiance_offsets')[band_names.split(",").index(band)]   
    else:
        print('REFLECTANCE OR RADIANCE NOT SPECIFIED')
        
    validmin = get_hdf_data(file, dataset, 'valid_range')[0]
    validmax = get_hdf_data(file, dataset, 'valid_range')[1]
    fillval = get_hdf_data(file, dataset, '_FillValue')
    
    # make mask of data, elminating "bad" data  
    # ---------------------------------------------------------------------
    # identify fill values or values outside valid range
    invalid = np.logical_or(band_data > validmax, band_data < validmin)
    invalid = np.logical_or(invalid, band_data == fillval)
    # replace these ^ with NaNs
    band_data[invalid] = np.nan
    # apply offset and scale
    band_data = (band_data - offsets) * scales 
    # make data a masked array to ignore NaNs in calculations
    band_data = np.ma.masked_array(band_data, np.isnan(band_data))
    
    return band_data

    
#////////////////////
#  get_MODISgeo  ///
#//////////////////
#---------------------------------------------------------------------
# Load lat, lon arrays from MODIS geo (hdf) files.
#---------------------------------------------------------------------
# DEPENDENCIES
from pyhdf.SD import SD, SDC
#---------------------------------------------------------------------
def get_MODISgeo(geofile):

    """Load lat, lon arrays from MODIS geo (hdf) files.
    Reads in Terra/MODIS (MOD03) or Aqua/MODIS (MOD03) geo files,
    May also work for hdf geolocation files from other satellites.
    Returns longitudes in range (0, 360).
    
INPUT:
- geofile: filename with directory  
           (e.g. '/Users/kenzie/MOD03.A2000059.1745.061.2017171195808.hdf')

OUTPUT:
- geolat: array of lat values
- geolon: array of lon values

DEPENDENCIES:
from pyhdf.SD import SD, SDC

Latest recorded update:
06-03-2022

    """
    
    # open geo file
    #--------------   
    try:
        f = SD(geofile,SDC.READ) 
    # raise an error if file can't be opened 
    except Exception as e:
        print(e, ", error opening ", geofile, sep='')

    # open geo file
    #--------------
    geolat = f.select(0)[:]       # pull out lat    
    geolon = f.select(1)[:]       # pull out lon 
    
    # make all longitudes range (0,360)
    #----------------------------------
    for i in range(0,geolon.shape[0]): 
         for j in range(0,geolon.shape[1]):
                if geolon[i,j] < 0:
                    geolon[i,j] = 360 + geolon[i,j]  
                    
    # close geo file and return lat, lon
    #-----------------------------------
    f.end() 
    
    return geolat, geolon


#/////////////////////
#  get_MODISdate  ///
#///////////////////
#---------------------------------------------------------------------
# Grab date from MODIS filename, create datetime object.
#---------------------------------------------------------------------
# DEPENDENCIES
import datetime as dt
from datetime import datetime
#---------------------------------------------------------------------
def get_MODISdate(filename):
    
    """Grab date from MODIS filename, create datetime object.
    MODIS filename can be from either geolocation or imagery files
    from level1b modis products, as long as they include date after
    '.A' in the filename.
    
INPUT:
- file: MODIS filename (without path) 
        (e.g. 'MOD021KM.A2006090.2150.061.2017263004124.hdf')

OUTPUT:
- imagedate: datetime object of MODIS image

DEPENDENCIES:
import datetime as dt
from datetime import datetime

Latest recorded update:
09-29-2022

    """
    
    # find beginning of date in filename
    #------------------------------------
    di = filename.index('.A')+2
    # grab year, day, hour, and minutes of image acquisition
    #---------------------------------------------------------
    YYYY = str(filename[di:di+4])
    DDD = str(filename[di+4:di+7])
    HH = str(filename[di+8:di+10])
    MM = str(filename[di+10:di+12])
    # create and return datetime object
    #----------------------------------
    imagedate = dt.datetime.strptime(YYYY+' '+DDD+' '+HH+' '+MM, '%Y %j %H %M')
    
    return imagedate

#////////////////////////
#  pair_images_meta  ///
#//////////////////////
#---------------------------------------------------------------------
# Load metadata of MODIS image files from folder.
#---------------------------------------------------------------------
# DEPENDENCIES
import glob
import os
import numpy as np
# homemade: 
# get_MODISdate
#---------------------------------------------------------------------

def pair_images_meta(MainFolder = [], SingleFolder = [], 
                     sensor = 'MODIS', 
                     satellite_labels = [('MOD03','MOD021KM'), ('MYD03','MYD021KM')], 
                     min_geofile_sizeMB = [], min_imfile_sizeMB = [],
                     max_diff_minutes = 20):
    
    """Load metadata of MODIS image files from folder. Pair geo and image and group by date.
    Does not open files, all operations done from file names so make sure
    the MODIS files are saved with the original names as downloaded from the LAADS DAAC
    
INPUT:
- MainFolder:main directory where subdirectories (one step down) contains images to check(default: []) 
- SingleFolder: directory where images are stored (default: []) 
- sensor: string describing sensor from satellite data (currently either 'VIIRS' for suomiNPP (.nc files) or 'MODIS' (.hdf) from NASA LAADS DAAC
- satellite_labels: list of tuples for geolocation and imagery tags for each satellite surce
                    (default: [('MOD03','MOD021KM'), ('MYD03','MYD021KM')] for Terra/MODIS, Aqua/MODIS)
- min_geofile_sizeMB: minimum accepted geofile size (in MB) without raising error
                      used to check for corrupted files which have too small of file size (normally > 28 MB)
                      (default: [] in which case it won't check file size)
- min_imfile_sizeMB: minimum accepted image file size (in MB) without raising error
                     used to check for corrupted files which have too small of file size (normally > 55 MB)
                     (default: [] in which case it won't check file size)
- max_diff_minutes: maximum time difference between images to use for pairing
                    (default: 20)

OUTPUT:
- Image_Meta_paired: M x 5 array of paired image metadata 
                     [date, geo_filename, image_filename, filepath, pair_index]
                     also paired images/dates are printed

DEPENDENCIES:
import glob
import os
import numpy as np
# homemade: 
from LIB_plot_VIIRS import get_VIIRS_date
from LIB_plot_MODIS import get_MODISdate

Latest recorded update:
10-07-2022

    """

    # assertions for input data
    #--------------------------
    assert sensor in ['MODIS', 'VIIRS'], f"Unrecognized satellite type, got: {sensor}"
        
    if str(sensor) == 'VIIRS':
        file_type = ".nc"
    elif str(sensor) == 'MODIS':
        file_type = ".hdf"
        
    Image_Meta = []
    
    # find all folders in main directory
    # or look in single folder provided
    if MainFolder != []:
        folder_list = glob.glob(MainFolder+"*/")
        print('Search within main folder: {}'.format(MainFolder))
    elif SingleFolder != []:
        folder_list = glob.glob(SingleFolder)
        print('Search in single folder: {}'.format(SingleFolder)) 

    # find list of hdf/nc files in each folder
    #--------------------------------------
    for folder in folder_list:
        # grab all hdf/nc files in folder and start empty
        # lists to fill with geo and image files
        #---------------------------------------------
        file_list = sorted(list(glob.glob1(folder, f"*{file_type}")));

        image_list,geo_list = [],[]
        # check for an even number of hdf/nc or nc files in folder
        # since num geo and image files should match
        #-----------------------------------------------
        if len(file_list)%2!=0:
            print(f'Odd number of {file_type} files found in folder. Should be one geo file per imagery file.')
            break
        # generate lists of geolocation and imagery files
        # run through filenames in file_list
        # for each type of satellite in satellite_labels:
        # if geolocation label in filename, add to geo_list
        # if imagery label in filename, add to geo_list
        #------------------------------------------------
        for file in file_list:  
            # grab size (MB) of file
            if min_geofile_sizeMB != [] and min_imfile_sizeMB != []:
                file_sizeMB = os.path.getsize(folder+file)/(1000**2) 
            for satellite in satellite_labels:
                if satellite[0] in file:
                    if min_geofile_sizeMB != []:
                        # if file size is less than given min_geofile_sizeMB, throw error since file
                        # was probably corrupted upon download. Usually 30-40 MB
                        if file_sizeMB < min_geofile_sizeMB:
                            print('{}\n{}\n{}'.format('='*len('POSSIBLE ERROR:'),'POSSIBLE ERROR:','='*len('POSSIBLE ERROR:')))
                            print('File {} is only {:.1f} MB, likely corrupted'.format(file,file_sizeMB))
                            break
                    geo_list.append(file)
                if satellite[1] in file:
                    if min_imfile_sizeMB != []:
                        # if file size is less than 55 MB, throw error since file
                        # was probably corrupted upon download. Usually 60+ MB
                        if file_sizeMB < min_imfile_sizeMB:
                            print('{}\n{}\n{}'.format('='*len('POSSIBLE ERROR:'),'POSSIBLE ERROR:','='*len('POSSIBLE ERROR:')))
                            print('File {} is only {:.1f} MB, likely corrupted\n'.format(file,file_sizeMB))
                            break
                    image_list.append(file)
                    
        # for each image, create list 
        # [date, geo_filename, image_filename, filepath]
        while len(geo_list)>0:
            # set current geo_file to first file in list
            # and delete geo_file from geo_list
            # and grab date from geo_file
            #-------------------------------------------
            geo_file = geo_list.pop(0)  
            
            if str(sensor) == 'VIIRS':
                ImageDate = get_VIIRS_date(geo_file)
            elif str(sensor) == 'MODIS':
                ImageDate = get_MODISdate(geo_file)
                
            # determine satellite source of geo_file
            #---------------------------------------
            for ii in range(len(satellite_labels)):
                if satellite_labels[ii][0] in geo_file:
                    satellite_image_source = satellite_labels[ii][1]
                    
            # search for matching imagery file
            # and delete it from image_list
            #---------------------------------
            ii = 0
            while len(image_list)>0: 
                # print error if search gets to end of list before finding a match
                if ii==len(image_list):
                    print('Date match could not be found for geo_file in image_list')
                    break
                # if satellite source matches geofile
                # check if imagery date matches geo_file
                # delete image_file from geo_list
                #------------------------------------
                if satellite_image_source in image_list[ii]:
                    if str(sensor) == 'VIIRS':
                        if get_VIIRS_date(image_list[ii])==ImageDate:
                            image_file = image_list.pop(ii)
                            break
                    elif str(sensor) == 'MODIS':
                        if get_MODISdate(image_list[ii])==ImageDate:
                            image_file = image_list.pop(ii)
                            break
                ii+=1
            Image_Meta.append([ImageDate, geo_file, image_file, folder])
    Image_Meta = sorted(Image_Meta)

    
    # FIND IMAGE PAIRS AND ADD PAIR_INDEX TO META
    #--------------------------------------------
    Image_Meta_paired = np.array([])
    pair_index = 0
    while len(Image_Meta)>0: 
        
        # pull current first image out of Image_Meta list
        # add a pair index to its metadata and add to Image_Meta_copy
        current_image = Image_Meta.pop(0)
        current_image.append(pair_index)
        Image_Meta_paired = np.append(Image_Meta_paired,current_image)
    
        
        # run through rest of images to search for pair
        # find difference in time between current image remaining images
        # if within max_diff_minutes mins, add to Image_Meta_copy with same pair_index
        indices_to_pair = []
        for check_image in Image_Meta:
            time_diff = np.abs(current_image[0]-check_image[0]).total_seconds()/60
            if time_diff <= max_diff_minutes: 
                indices_to_pair.append(Image_Meta.index(check_image))
        
        images_to_add_to_pair = np.array([])
        # in reverse order, pop paired values from Image_Meta
        for current_index in indices_to_pair[::-1]:
            pair_image = Image_Meta.pop(current_index)
            pair_image.append(pair_index)
            images_to_add_to_pair = np.append(images_to_add_to_pair, pair_image)
        images_to_add_to_pair = np.reshape(images_to_add_to_pair, [int(len(indices_to_pair)),5])
        
        # in original sequential order, add to to Image_Meta_paired with correct index
        for pair_image in images_to_add_to_pair[::-1]:
            Image_Meta_paired = np.append(Image_Meta_paired,pair_image)
                
        # move on to next of remaining images
        pair_index+=1
        
    Image_Meta_paired = np.reshape(Image_Meta_paired,[int(len(Image_Meta_paired)/5),5])

    # print image dates by pairs
    #---------------------------
    num_pairs = np.max(Image_Meta_paired[:,4])+1
    for ii in range(num_pairs):
        print('Pair {}\n------'.format(ii))
        for jj in np.where(Image_Meta_paired[:,4] ==ii)[0]:
            print(Image_Meta_paired[jj,0])
        print()
        
        
    return Image_Meta_paired

