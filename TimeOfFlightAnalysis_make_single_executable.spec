# -*- mode: python ; coding: utf-8 -*-

from sys import platform as _platform

import os
from distutils.sysconfig import get_python_lib
import sys

import scipy


scipy_libs = os.path.join(os.path.dirname(scipy.__file__), '.libs')

sys.setrecursionlimit(5000)

folder = os.getcwd()
site_packages_path = get_python_lib()
print(folder)

block_cipher = None
from sys import platform as _platform




platform = ''
extra_binaries=[]
#folder = ''

if _platform == "linux" or _platform == "linux2":
    platform = "Linux"
    name = "TimeOfFlight"
elif _platform == "win32" or _platform == "cygwin":
    platform = "Win"
    name = "TimeOfFlight.exe"
    sys.path.append("C:\\Users\\hrubiak\\Documents\\GitHub\\sonicPy")
    extra_datas = [
        ("ua\\resources", "ua\\resources"),
        ("um\\resources", "um\\resources"),
        ("dask", "dask")
    ]
 
elif _platform == "darwin":
    platform = "Mac"
    extra_binaries=[ ]
    name = "run_TimeOfFlight"
    sys.path.append("/Users/ross/GitHub/sonicPy")
    extra_datas = [
        ("ua/resources", "ua/resources"),
        ("dask", "dask")
    ]

import ua

# checking whether the platform is 64 or 32 bit
if sys.maxsize > 2 ** 32:
    platform += "64"
else:
    platform += "32"


excl = ['matplotlib', 'PySide','PyQt4','pyeqt']


print('start Analysis')

a = Analysis(['TimeOfFlightAnalysis.py'],
             pathex=[scipy_libs],
             binaries=extra_binaries,
             datas=extra_datas,
             hiddenimports=[
                            "ua"
                            ],
             hookspath=[],
             runtime_hooks=[],
             excludes=excl,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# remove packages which are not needed by Dioptas
a.binaries = [x for x in a.binaries if not x[0].startswith("matplotlib")]
a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]
a.binaries = [x for x in a.binaries if not x[0].startswith("IPython")]
a.binaries = [x for x in a.binaries if not x[0].startswith("docutils")]
a.binaries = [x for x in a.binaries if not x[0].startswith("pytz")]
a.binaries = [x for x in a.binaries if not x[0].startswith("wx")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libQtWebKit")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libQtDesigner")]
a.binaries = [x for x in a.binaries if not x[0].startswith("PySide")]
a.binaries = [x for x in a.binaries if not x[0].startswith("libtk")]

exclude_datas = [
    "IPython",
   "matplotlib",
#   "mpl-data", #needs to be included
   "_MEI",
   "docutils",
   "pytz",
#   "lib",
   "include",
   "sphinx",
   ".py",
   "tests",
   "skimage",
   "alabaster",
   "boto",
   "jsonschema",
   "babel",
   "idlelib",
   "requests",
   "qt4_plugins",
   "qt5_plugins"
]

for exclude_data in exclude_datas:
    a.datas = [x for x in a.datas if exclude_data not in x[0]]



pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)


from ua import __version__
print('version ' + __version__)



exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='TimeOfFlight_{}_{}'.format(platform, __version__),
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )

if _platform == "darwin":
    coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
                onefile=True,
               name='TimeOfFlight_{}_{}'.format(platform, __version__))

    app = BUNDLE(coll,
                 name='TimeOfFlight_{}.app'.format(__version__),
                 #icon='ua/resources/icons/icon.icns',
                 bundle_identifier=None,
                 info_plist={
                    'NSPrincipalClass': 'NSApplication',
                    'NSAppleScriptEnabled': False,
                    'NSHighResolutionCapable': True,
                    'LSBackgroundOnly': False
                    }
                 
                 )