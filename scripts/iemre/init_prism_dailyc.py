"""Generate the PRISM climatology file, hmmm"""
from __future__ import print_function
import datetime

import numpy as np
from pyiem import prism
from pyiem.util import ncopen

BASEDIR = "/mesonet/data/prism"


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fn = "%s/prism_dailyc.nc" % (BASEDIR,)
    nc = ncopen(fn, "w")
    nc.title = "PRISM Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "PRISM"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
        datetime.datetime.now().strftime("%d %B %Y"),
    )
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", prism.NY)
    nc.createDimension("lon", prism.NX)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))
    nc.createDimension("nv", 2)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", np.float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = prism.YAXIS

    lat_bnds = nc.createVariable("lat_bnds", np.float, ("lat", "nv"))
    lat_bnds[:, 0] = prism.YAXIS
    lat_bnds[:, 1] = prism.YAXIS + 0.04

    lon = nc.createVariable("lon", np.float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = prism.XAXIS

    lon_bnds = nc.createVariable("lon_bnds", np.float, ("lon", "nv"))
    lon_bnds[:, 0] = prism.XAXIS
    lon_bnds[:, 1] = prism.XAXIS + 0.04

    tm = nc.createVariable("time", np.float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "ppt", np.float, ("time", "lat", "lon"), fill_value=1.0e20
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    high = nc.createVariable(
        "tmax", np.float, ("time", "lat", "lon"), fill_value=-9999.0
    )
    high.units = "C"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "tmin", np.float, ("time", "lat", "lon"), fill_value=-9999.0
    )
    low.units = "C"
    low.long_name = "2m Air Temperature Daily High"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    nc.close()


def main():
    """Go Main"""
    init_year(datetime.datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
