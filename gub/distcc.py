#!/usr/bin/env python2

import os
import re
import socket
import sys
import telnetlib
#
from gub.syntax import printf

def live_hosts (hosts, port = 3633):
    live = []
    for h in hosts:
        try:
            t = telnetlib.Telnet (h, port)
            t.close ()
        except socket.error:
            continue

        live.append ('%s:%d' % (h,port))

    if live:
        printf ('DISTCC live hosts: ', live)
    return live


def main ():
    exe_name = os.path.split (sys.argv[0])[1]
    path_comps = [c for c in os.environ['PATH'].split (':')
                  if not re.search ('distcc', c)]
    os.environ['PATH'] = ':'.join (path_comps)
    argv = ['distcc', exe_name] + sys.argv[1:]
    os.execvp ('distcc', argv)

if __name__ == '__main__':
    main ()

