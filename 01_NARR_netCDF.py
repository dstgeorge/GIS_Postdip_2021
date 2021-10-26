# --------------------------------------------
# Name: David St. George
# Date: 2021-05-03
# File Name: 01_NARR_netCDF
# --------------------------------------------

# Using NARR NetCDF uwnd & vwnd files, complete the following:
# - merge ALL YEARS into a single NETCDF file
# - complete wind speed magnitude calculation
# - convert from m/s to km/hr

import xarray as xr
import xarray.ufuncs as xu


def main():

    print(f'Combining NARR datasets')
    wind = xr.open_mfdataset("../../NARR_DATA/*wnd.10m.*.nc")

    # Compute Wind Speed Magnitude
    wnd_spd_mag = xu.sqrt(wind.uwnd**2+wind.vwnd**2)

    # Convert from m/s to km/hr
    wnd_spd_mag = wnd_spd_mag*3.6

    wnd_spd_mag = wnd_spd_mag.to_dataset(name='wnd_spd_mag')

    wnd_spd_mag_mean = wnd_spd_mag.resample(time='3MS', label='left',
                                            closed='left').mean()

    wnd_spd_mag_max = wnd_spd_mag.resample(time='3MS', label='left',
                                           closed='left').max()

    wnd_spd_mag_mean.to_netcdf(
        f"../../NARR_DATA/SEASONAL/NARR_combined_mean.nc",
        encoding={'wnd_spd_mag':{'zlib':True}})

    wnd_spd_mag_max.to_netcdf(
        f"../../NARR_DATA/SEASONAL/NARR_combined_max.nc",
        encoding={'wnd_spd_mag':{'zlib':True}})

main()
