import rasterio
from pyproj import Proj, transform
import glob
import pandas as pd

def lat_lon_to_pixel(geotiff_file, lat, lon):
    # Define the projection of the geotiff file
    with rasterio.open(geotiff_file) as src:
        src_proj = Proj(src.crs)

        # Convert lat/lon to the coordinate system of the geotiff file
        x, y = transform(Proj(init='epsg:4326'), src_proj, lon, lat)

        # Convert coordinates to pixel indices
        px, py = src.index(x, y)
        
        # Round to nearest integer pixel
        px = int(round(px))
        py = int(round(py))
        
        return px, py

def extract_pixel_value(geotiff_file, px, py):
    with rasterio.open(geotiff_file) as src:
        if 0 <= px < src.width and 0 <= py < src.height:
            value = src.read(1, window=((py, py+1), (px, px+1)))
            return value[0][0]
        else:
            print("Coordinates out of bounds.")
            return None

location = 'Goodwin Creek'
lat = 34.2547
lon = -89.8729

path = f'E:/Sentinel3Work/New_Data/{location}/Results/'
Folder_path = glob.glob(f'{path}*')
df = pd.DataFrame(columns=['Date', 'LSE1', 'RLST [K]', 'SLST [K]'])

for Jpath in Folder_path:
    LSE_tiff = f'{Jpath}/LSE_B8.tif'
    my_tiff = glob.glob(f'{Jpath}/RLST*.tif')
    your_tiff = glob.glob(f'{Jpath}/*SLST.tif')
    # Example usage:
    if not my_tiff:
        print('list is empty')
    else:
        #retrieved LST extraction
        geotiff_file = my_tiff[0]
        px, py = lat_lon_to_pixel(geotiff_file, lat, lon)
        pixel_value = extract_pixel_value(geotiff_file, px, py) #retrieved LST value variable
        #Sentinel3 LST product extraction
        geotiff_file_SLST = your_tiff[0]
        pixel_value1 = extract_pixel_value(geotiff_file_SLST, px, py) #Sentinel LST product value variable
        #LSE value
        geotiff_file_LSE = LSE_tiff
        pixel_value2 = extract_pixel_value(geotiff_file_LSE, px, py)
        #saving values
        date=geotiff_file[-19:-4]
        lst_value = pixel_value
        slst_value = pixel_value1
        lse_value = pixel_value2
        df.loc[len(df)] = [date, lse_value, lst_value, slst_value]
        print("Pixel value at latitude {} and longitude {}: {}".format(lat, lon, pixel_value))

df.to_excel(f'{path}{location}_satellite_LST_final.xlsx', index=False)
