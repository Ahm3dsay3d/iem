"""
Need to do some custom 1 minute data aggregation to fill out hourly table.
"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc, logger

LOG = logger()
TIME_FORMAT = "%Y-%m-%d %H:%M-06"


def do_updates(cursor, station, row):
    """Make the updates happen, captain."""
    cursor.execute(
        """
        UPDATE sm_hourly SET
        slrmj_tot = coalesce(%(slrkj_tot_sum)s, 0) / 1000.,
        slrmj_tot_qc = coalesce(%(slrkj_tot_sum)s, 0) / 1000.,
        slrkw_avg = coalesce(%(slrkj_tot_sum)s, 0) / 3600.,
        slrkw_avg_qc = coalesce(%(slrkj_tot_sum)s, 0) / 3600.,
        tair_c_avg = %(tair_c_avg)s,
        tair_c_avg_qc = %(tair_c_avg)s,
        tsoil_c_avg = %(tsoil_c_avg)s,
        tsoil_c_avg_qc = %(tsoil_c_avg)s,
        calc_vwc_12_avg = %(calc_vwc_12_avg)s,
        calc_vwc_12_avg_qc = %(calc_vwc_12_avg)s,
        calc_vwc_24_avg = %(calc_vwc_24_avg)s,
        calc_vwc_24_avg_qc = %(calc_vwc_24_avg)s,
        calc_vwc_50_avg = %(calc_vwc_50_avg)s,
        calc_vwc_50_avg_qc = %(calc_vwc_50_avg)s,
        t12_c_avg = %(t12_c_avg)s,
        t12_c_avg_qc = %(t12_c_avg)s,
        t24_c_avg = %(t24_c_avg)s,
        t24_c_avg_qc = %(t24_c_avg)s,
        t50_c_avg = %(t50_c_avg)s,
        t50_c_avg_qc = %(t50_c_avg)s,
        obs_count = %(obs_count)s
        WHERE station = %(station)s and valid = %(valid_cst)s
    """,
        row,
    )
    if cursor.rowcount == 0:
        LOG.debug(
            "Updating %s %s resulted in 0 rows updated",
            station,
            row["valid_cst"],
        )


def hourly_process(cursor, row):
    """Merge this row information into the database."""
    # Data for this 'hour' is stored at the top of the next hour in the
    # database
    valid_cst = row["hour"] + datetime.timedelta(hours=1)
    row["valid_cst"] = valid_cst.strftime(TIME_FORMAT)
    station = row["station"]
    cursor.execute(
        """
        SELECT obs_count from sm_hourly where station = %s and valid = %s
    """,
        (station, row["valid_cst"]),
    )
    if cursor.rowcount == 1:
        current = cursor.fetchone()
        if current[0] == row["obs_count"]:
            LOG.debug(
                "%s %s obs_count %s matches",
                row["valid_cst"],
                station,
                row["obs_count"],
            )
            return
    elif cursor.rowcount == 0:
        # Need to create an entry
        cursor.execute(
            """
        INSERT into sm_hourly(station, valid, obs_count) values (%s, %s, 0)
        """,
            (station, row["valid_cst"]),
        )
    do_updates(cursor, station, row)


def daily_process(cursor, station, date, df):
    """Process this date's dataframe."""
    sumdf = df.sum()
    avgdf = df.mean()
    row = {"station": station, "date": date}
    row["obs_count"] = float(sumdf["obs_count"])
    for colname in [
        "tsoil_c_avg",
        "t12_c_avg",
        "t24_c_avg",
        "t50_c_avg",
        "calc_vwc_12_avg",
        "calc_vwc_24_avg",
        "calc_vwc_50_avg",
    ]:
        row[colname] = float(avgdf[colname])
    cursor.execute(
        """
        SELECT obs_count from sm_daily where station = %s and valid = %s
    """,
        (station, date),
    )
    if cursor.rowcount == 0:
        LOG.debug("no database entry found %s %s", date, station)
        return
    current = cursor.fetchone()
    if current[0] == row["obs_count"]:
        LOG.debug(
            "%s %s obs_count %s matches", date, station, row["obs_count"]
        )
        return
    cursor.execute(
        """
        UPDATE sm_daily SET
        tsoil_c_avg = %(tsoil_c_avg)s,
        tsoil_c_avg_qc = %(tsoil_c_avg)s,
        t12_c_avg = %(t12_c_avg)s,
        t12_c_avg_qc = %(t12_c_avg)s,
        t24_c_avg = %(t24_c_avg)s,
        t24_c_avg_qc = %(t24_c_avg)s,
        t50_c_avg = %(t50_c_avg)s,
        t50_c_avg_qc = %(t50_c_avg)s,
        calc_vwc_12_avg = %(calc_vwc_12_avg)s,
        calc_vwc_12_avg_qc = %(calc_vwc_12_avg)s,
        calc_vwc_24_avg = %(calc_vwc_24_avg)s,
        calc_vwc_24_avg_qc = %(calc_vwc_24_avg)s,
        calc_vwc_50_avg = %(calc_vwc_50_avg)s,
        calc_vwc_50_avg_qc = %(calc_vwc_50_avg)s,
        vwc_12_avg = %(calc_vwc_12_avg)s,
        vwc_12_avg_qc = %(calc_vwc_12_avg)s,
        vwc_24_avg = %(calc_vwc_24_avg)s,
        vwc_24_avg_qc = %(calc_vwc_24_avg)s,
        vwc_50_avg = %(calc_vwc_50_avg)s,
        vwc_50_avg_qc = %(calc_vwc_50_avg)s,
        obs_count = %(obs_count)s
        WHERE station = %(station)s and valid = %(date)s
    """,
        row,
    )


def workflow():
    """Do things."""
    pgconn = get_dbconn("isuag")
    # We need to collect up data for periods representing CST dates, this
    # is tricky business
    date = datetime.date.today() - datetime.timedelta(days=7)
    # 6z is the start of such a date
    sts = utc(date.year, date.month, date.day, 6)
    df = read_sql(
        """
    WITH data as (
        SELECT *,
        date_trunc('hour',
            (valid - '1 minute'::interval) at time zone 'UTC+6') as hour,
        row_number() OVER (
            PARTITION by station,
            date_trunc('hour',
            (valid - '1 minute'::interval) at time zone 'UTC+6')
            ORDER by valid DESC) as rn
        from sm_minute where valid >= %s
    )
    SELECT
    station, hour,
    count(*) as obs_count,
    sum(slrkj_tot_qc) as slrkj_tot_sum,
    max(case when rn = 1 then tair_c_avg else null end) as tair_c_avg,
    max(case when rn = 1 then tsoil_c_avg else null end) as tsoil_c_avg,
    max(case when rn = 1 then t12_c_avg else null end) as t12_c_avg,
    max(case when rn = 1 then t24_c_avg else null end) as t24_c_avg,
    max(case when rn = 1 then t50_c_avg else null end) as t50_c_avg,
    max(case when rn = 1 then calcVWC12_Avg else null end) as calc_vwc_12_avg,
    max(case when rn = 1 then calcVWC24_Avg else null end) as calc_vwc_24_avg,
    max(case when rn = 1 then calcVWC50_Avg else null end) as calc_vwc_50_avg
    from data GROUP by station, hour
    """,
        pgconn,
        params=(sts,),
        index_col=None,
    )
    # Compute the "date"
    df["date"] = df["hour"].dt.date
    # We want NaN values as None
    df = df.replace({np.nan: None})

    # Daily work
    cursor = pgconn.cursor()
    for (station, date), gdf in df.groupby(["station", "date"]):
        daily_process(cursor, station, date, gdf)
    cursor.close()
    pgconn.commit()

    # Hourly work
    cursor = pgconn.cursor()
    for _, row in df.iterrows():
        hourly_process(cursor, row)
    cursor.close()
    pgconn.commit()


def main():
    """Go Main Go."""
    workflow()


if __name__ == "__main__":
    main()
