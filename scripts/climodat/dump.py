"""Dump!"""
import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

BASEDIR = "/mesonet/share/pickup/coop_data"


def main():
    """Go Main Go"""
    nt = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop", user="nobody")
    ccursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    for sid in nt.sts:
        fn = "%s/%s.csv" % (BASEDIR, nt.sts[sid]["name"].replace(" ", "_"))
        out = open(fn, "w")
        out.write("station,station_name,lat,lon,day,high,low,precip,snow,\n")
        ccursor.execute(
            """
            SELECT * from alldata_ia WHERE station = %s ORDER by day ASC
        """,
            (sid,),
        )

        for row in ccursor:
            out.write(
                ("%s,%s,%s,%s,%s,%s,%s,%s,%s,\n")
                % (
                    sid.lower(),
                    nt.sts[sid]["name"],
                    nt.sts[sid]["lat"],
                    nt.sts[sid]["lon"],
                    row["day"],
                    row["high"],
                    row["low"],
                    row["precip"],
                    row["snow"],
                )
            )

        out.close()


if __name__ == "__main__":
    main()
