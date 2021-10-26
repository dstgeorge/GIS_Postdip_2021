# --------------------------------------------
# Name: David St. George
# Date: 2021-05-06
# File Name: 01_ECMWF_netCDF
# --------------------------------------------

# Using ECMWF NetCDF uwnd & vwnd files, complete the following:
# - merge into a single NETCDF file
# - complete wind speed magnitude calculation
# - convert from m/s to km/hr
# - extract a daily mean from hourly values

import xarray as xr
import xarray.ufuncs as xu

def main():
    print(f'Combining ECMWF datasets')

    wnd = xr.open_mfdataset("../ARENA/RAW_DATA/ECMWF/ECMWF_*.nc")
    # Compute Wind Speed Magnitude
    wnd_spd_mag = xu.sqrt(wind.u10**2+wind.v10**2)

    # Convert from m/s to km/hr
    wnd_spd_mag = wnd_spd_mag*3.6

    wnd_spd_mag = wnd_spd_mag.to_dataset(name='wnd_spd_mag')

    wnd_spd_mag = wnd_spd_mag.resample(time='3MS', label='left',
                                       closed='left',
                                       restore_coord_dims=True).mean()

    # NOTE: MODIFIED FOR SEASONAL RESAMPLING 10-MAY-21
    wnd_spd_mag.to_netcdf(f"../../ECMWF_DATA/SEASONAL/ECMWF_combined.nc",
                          encoding={'wnd_spd_mag':{'zlib':True}})

main()