import os
import re
import darwintools
import context

class Installer (context.Os_context_wrapper):
	def __init__ (self, settings):
		context.Os_context_wrapper.__init__ (self, settings)
		
		self.settings = settings
		self.strip_command = self.settings.target_architecture + "-strip"
		self.no_binary_strip = []

	@subst_method
        def name (self):
		return 'lilypond'

	def build (self):
		return self.settings.bundle_build

	@subst_method
	def version (self):
		return self.settings.bundle_version

	def strip_prefixes (self):
		return ['', 'usr/']
		
	def strip_unnecessary_files (self):
		"Remove unnecessary cruft."

		delete_me = ''
		for p in self.strip_prefixes ():
			delete_me += p + '%(i)s '

		for i in (
			'bin/autopoint',
			'bin/glib-mkenums',
			'bin/guile-*',
			'bin/*-config',
			'bin/*gettext*',
			'bin/[cd]jpeg',
			'bin/envsubst*',
			'bin/glib-genmarshal*',
			'bin/gobject-query*',
			'bin/gspawn-win32-helper*',
			'bin/gspawn-win32-helper-console*',
			'bin/msg*',
			'bin/pango-querymodules*',
			'bin/python*',
			'bin/python%(python_version)s*',
			'bin/xmlwf',
			'doc',
			'include',
			'info',
			'lib/gettext',
			'lib/gettext/hostname*',
			'lib/gettext/urlget*',
			'lib/glib-2.0/include/glibconfig.h',
			'lib/glib-2.0',
			'lib/pkgconfig',
			'lib/*~',
			'lib/*.a',
			'lib/python2.4/distutils/command/wininst-6*',
			'lib/python2.4/distutils/command/wininst-7.1*',
			'man',
			'share/doc',
			'share/gettext/intl',
			'share/ghostscript/8.15/Resource/',
			'share/ghostscript/8.15/doc/',
			'share/ghostscript/8.15/examples',
			'share/gs/8.15/Resource/',
			'share/gs/8.15/doc/',
			'share/gs/8.15/examples',
			'share/gtk-doc',
			'share/info',
			'share/man',
			'share/omf',

			# prune harder
			'lib/python%(python_version)s/bsddb',
			'lib/python%(python_version)s/compiler',
			'lib/python%(python_version)s/curses',
			'lib/python%(python_version)s/distutils',
			'lib/python%(python_version)s/email',
			'lib/python%(python_version)s/hotshot',
			'lib/python%(python_version)s/idlelib',
			'lib/python%(python_version)s/lib-old',
			'lib/python%(python_version)s/lib-tk',
			'lib/python%(python_version)s/logging',
			'lib/python%(python_version)s/test',
			'lib/python%(python_version)s/xml',
			'share/lilypond/*/make',
			'share/gettext',
			'usr/share/aclocal',
			'share/lilypond/*/python',
			'share/lilypond/*/tex',
			'share/lilypond/*/vim',
			'share/lilypond/*/python',
			'share/lilypond/*/fonts/source',
			'share/lilypond/*/fonts/svg',
			'share/lilypond/*/fonts/tfm',
			'share/locale',
			'share/omf',
			'share/gs/fonts/[a-bd-z]*',
			'share/gs/fonts/c[^0][^9][^5]*',
			'share/gs/Resource',			
			):

			self.system ('cd %(installer_root)s && rm -rf ' + delete_me, {'i': i })

	def strip_binary_file (self, file):
		self.system ('%(strip_command)s %(file)s', locals (), ignore_error = True)

	def strip_binary_dir (self, dir):
		(root, dirs, files) = os.walk (dir % self.get_substitution_dict ()).next ()
		for f in files:
			if os.path.basename (f) not in self.no_binary_strip:
				self.strip_binary_file (root + '/' + f)
			
	def strip (self):
		self.strip_unnecessary_files ()
		self.strip_binary_dir ('%(installer_root)s/usr/lib')
		self.strip_binary_dir ('%(installer_root)s/usr/bin')
		
	def create (self):
		self.strip ()
		
class Darwin_bundle (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -S '

	def create (self):
		Installer.create (self)
		rw = darwintools.Rewirer (self.settings)
		rw.rewire_root (self.settings.installer_root)
		
	def strip (self):
		self.strip_unnecessary_files ()
		# no binary strip: makes debugging difficult.
		
class Nsis (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -g '
		self.no_binary_strip = ['gsdll32.dll', 'gsdll32.lib']
		
	def create (self):
		Installer.create (self)
		
		# FIXME: build in separate nsis dir, copy or use symlink
		installer = os.path.basename (self.settings.installer_root)
		self.file_sub ([
			('@GUILE_VERSION@', '%(guile_version)s'),
			('@LILYPOND_BUILD@', '%(bundle_build)s'),
			('@LILYPOND_VERSION@', '%(bundle_version)s'),
			('@PYTHON_VERSION@', '%(python_version)s'),
			('@ROOT@', '%(installer)s'),
			],
			       '%(nsisdir)s/lilypond.nsi.in',
#			       to_name='%(targetdir)s/lilypond.nsi',
			       to_name='%(targetdir)s/lilypond.nsi',
			       env=locals ())
		# FIXME: move nsis cruft to nsis dir
		self.system ('cp %(nsisdir)s/*.nsh %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.scm.in %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.sh.in %(targetdir)s')
		self.system ('cd %(targetdir)s && makensis lilypond.nsi')
#		self.system ('cd %(targetdir)s && makensis -NOCD %(nsisdir)/lilypond.nsi')
		self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/lilypond-%(bundle_version)s-%(build)s.exe', locals ())

class Linux_installer (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		# lose the i486-foo-bar-baz-
		self.strip_command = 'strip -g'

	def strip_prefixes (self):
		return (Installer.strip_prefixes (self)
			+ [self.expand ('%(framework_dir)s/usr/')])
			
	def strip (self):
		Installer.strip (self)
		self.strip_binary_dir ('%(installer_root)s/usr/lib/lilypond/%(bundle_version)s/lib/usr/bin')
		self.strip_binary_dir ('%(installer_root)s/usr/lib/lilypond/%(bundle_version)s/lib/usr/lib')

class Tgz (Linux_installer):
	def create (self):
		Linux_installer.create (self)
		build = self.settings.bundle_build
		self.system ('tar -C %(installer_root)s -zcf %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(build)s.tgz .', locals ())

class Deb (Linux_installer):
	def create (self):
		build = self.settings.bundle_build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(build)s.tgz', locals ())

class Rpm (Linux_installer):
	def create (self):
		build = self.settings.bundle_build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(build)s.tgz', locals ())

class Autopackage (Linux_installer):
	def create (self):
		self.system ('rm -rf %(build_autopackage)s')
		self.system ('mkdir -p %(build_autopackage)s/autopackage')
		self.file_sub ([('@VERSION@', '%(bundle_version)s')],
			       '%(specdir)s/lilypond.apspec.in',
			       to_name='%(build_autopackage)s/autopackage/default.apspec')
		# FIXME: just use symlink?
		self.system ('tar -C %(installer_root)s/usr -cf- . | tar -C %(build_autopackage)s -xvf-')
		self.system ('cd %(build_autopackage)s && makeinstaller')
		self.system ('mv %(build_autopackage)s/*.package %(installer_uploads)s')


def get_installers (settings):
	installers = {
		'darwin' : [Darwin_bundle (settings)],
		'linux' : [
		Tgz (settings),
		Deb (settings),
		Rpm (settings),
		Autopackage (settings),
		],
		'mingw' : [Nsis (settings)],
	}

	return installers[settings.platform]
