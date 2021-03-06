from gub import target
from gub import tools

class G_wrap (target.AutoBuild):
    dependencies = [
        'glib',
        'guile',
        'libffi',
        'tools::g-wrap',
        ]
    source = 'http://download.savannah.gnu.org/releases/g-wrap/g-wrap-1.9.13.tar.gz'
    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([('-std=gnu99', '')], '%(builddir)s/guile/g-wrap/Makefile')
        self.file_sub ([('///', '/')], '%(builddir)s/lib/Makefile', must_succeed=True)
    parallel_build_broken = True
    def install (self):
        target.AutoBuild.install (self)
        self.dump ('''
(define (get-prefix-dir) (dirname (dirname (car (command-line)))))
(define *g-wrap-shlib* (string-append (get-prefix-dir) "/lib/g-wrap/modules/"))
''',
                   '%(install_prefix)s/share/guile/site/g-wrap/config.scm',
                   mode='a')
    
class G_wrap__mingw (G_wrap):
    def configure (self):
        G_wrap.configure (self)
        for i in ('%(builddir)s/guile/g-wrap/Makefile',
                  '%(builddir)s/guile/Makefile', # localtime_r
                  '%(builddir)s/guile/examples/Makefile', # localtime_r
                  '%(builddir)s/g-wrap/Makefile',
                  '%(builddir)s/lib/Makefile'):
            self.file_sub ([('-Werror', '')], i, must_succeed=True)

class G_wrap__tools (tools.AutoBuild, G_wrap):
    def configure (self):
        tools.AutoBuild.configure (self)
        for i in ('%(builddir)s/guile/g-wrap/Makefile',
                  '%(builddir)s/lib/Makefile'):
            self.file_sub ([('-std=gnu99', '')], i)
