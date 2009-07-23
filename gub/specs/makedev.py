from gub import tools

class Makedev__tools (tools.MakeBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/m/makedev/makedev_3.3.8.2.orig.tar.gz'
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s/%(system_root)s install'''

