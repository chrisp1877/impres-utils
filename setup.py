from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('src/main.py', base=base, targetName = 'impresys-utils')
]

setup(name='Impresys Utils',
      version = '0.1',
      description = 'Utilities for Impresys DemoMates demos',
      options = dict(build_exe = buildOptions),
      executables = executables)
