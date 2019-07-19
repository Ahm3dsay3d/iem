#!/usr/bin/env python
"""Frontend for Feature Content, such that we can make some magic happen"""
import sys
import os
import re
import datetime

from pyiem.util import get_dbconn, ssw

PATTERN = re.compile(("^/onsite/features/(?P<yyyy>[0-9]{4})/(?P<mm>[0-9]{2})/"
                      "(?P<yymmdd>[0-9]{6})(?P<extra>.*)."
                      "(?P<suffix>png|gif|jpg|xls|pdf|gnumeric|mp4)$"))


def send_content_type(val, totalsize=0, stripe=None):
    """Do as I say"""
    ssw("Accept-Ranges: bytes\n")
    if totalsize != (stripe.stop - stripe.start):
        ssw("Status: 206 Partial Content\n")
    if stripe:
        ssw("Content-Length: %.0f\n" % (stripe.stop - stripe.start, ))
    if os.environ.get("HTTP_RANGE") and stripe is not None:
        secondval = (
            ""
            if os.environ.get("HTTP_RANGE") == 'bytes=0-'
            else (stripe.stop - 1)
        )
        ssw("Content-Range: bytes %s-%s/%s\n" % (
            stripe.start, secondval, totalsize))
    if val == 'text':
        ssw("Content-type: text/plain\n\n")
    elif val in ['png', 'gif', 'jpg']:
        ssw("Content-type: image/%s\n\n" % (val, ))
    elif val in ['mp4', ]:
        ssw("Content-type: video/%s\n\n" % (val, ))
    elif val in ['pdf', ]:
        ssw("Content-type: application/%s\n\n" % (val, ))
    else:
        ssw("Content-type: text/plain\n\n")


def dblog(yymmdd):
    """Log this request"""
    try:
        pgconn = get_dbconn("mesosite")
        cursor = pgconn.cursor()
        dt = datetime.date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]),
                           int(yymmdd[4:6]))
        cursor.execute("""
            UPDATE feature SET views = views + 1
            WHERE date(valid) = %s
            """, (dt,))
        pgconn.commit()
    except Exception as exp:
        sys.stderr.write(str(exp))


def process(env):
    """Process this request

    This should look something like "/onsite/features/2016/11/161125.png"
    """
    uri = env.get('REQUEST_URI')
    if uri is None:
        send_content_type("text")
        ssw("ERROR!")
        return
    match = PATTERN.match(uri)
    if match is None:
        send_content_type("text")
        ssw("ERROR!")
        sys.stderr.write("feature content failure: %s\n" % (repr(uri), ))
        return
    data = match.groupdict()
    fn = ("/mesonet/share/features/%(yyyy)s/%(mm)s/"
          "%(yymmdd)s%(extra)s.%(suffix)s") % data
    if os.path.isfile(fn):
        rng = env.get("HTTP_RANGE", "bytes=0-")
        tokens = rng.replace("bytes=", "").split("-", 1)
        resdata = open(fn, 'rb').read()
        totalsize = len(resdata)
        stripe = slice(
            int(tokens[0]),
            totalsize if tokens[-1] == '' else (int(tokens[-1]) + 1))
        send_content_type(data['suffix'], len(resdata), stripe)
        ssw(resdata[stripe])
        dblog(data['yymmdd'])
    else:
        send_content_type('png')
        from io import BytesIO
        from pyiem.plot.use_agg import plt
        (_, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Feature Image was not Found!",
                transform=ax.transAxes, ha='center')
        plt.axis('off')
        ram = BytesIO()
        plt.savefig(ram, format='png')
        ram.seek(0)
        ssw(ram.read())


def main():
    """Do Something"""
    process(os.environ)


if __name__ == '__main__':
    main()
