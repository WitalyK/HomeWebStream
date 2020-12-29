# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('webstreaming.py',
                          targetName='webstreaming.exe',
                          #base='Win32GUI',
                          icon='belka.png')]

#excludes = ['logging', 'unittest', 'email', 'html', 'http', 'urllib', 'xml',
#            'unicodedata', 'bz2', 'select']

includes = ['encodings', 'importlib']

include_files = ['pyimagesearch', 'templates', 'ui_mainform.py']

options = {
    'build_exe': {
        'include_msvcr': True,
        #'excludes': excludes,
        #'zip_include_packages': zip_include_packages,
		'includes': includes,
        'build_exe': 'build_windows',
		'include_files': include_files,
    }
}

setup(name='belka',
      version='0.0.1',
      description="how's the cat?",
      executables=executables,
      options=options)