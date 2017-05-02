version = '1.87'


message('Getting python directiories')

python = find_program('python3')
pythondetector = find_program('../scripts/pythondetector')
python_dep = dependency('python3')

cres = run_command(pythondetector, '--sosuffix')
if cres.returncode() != 0
    error('Could not detect python sosuffix' + cres.stdout() + cres.stderr())
endif
py_so_suffix = cres.stdout().strip()

cres = run_command(pythondetector, '--abiflags')
if cres.returncode() != 0
    error('Could not detect python abiflags' + cres.stdout() + cres.stderr())
endif
python_abi_flags = cres.stdout().strip()

cres = run_command(pythondetector, '--libloc')
if cres.returncode() != 0
    error('Could not detect python library location' + cres.stdout() + cres.stderr())
endif
pylib_loc = cres.stdout().strip()

assert(pylib_loc != 'None', 'Python dynamic library path could not be determined')

pylib_suffix = 'so'
if host_machine.system() == 'windows'
  pylib_suffix = 'dll'
elif host_machine.system() == 'darwin'
  pylib_suffix = 'dylib'
endif
# Configuration params

cdata = configuration_data()
cdata.set('PACKAGE', '"Remarkable"')
# Configuration params
cdata.set('PACKAGE_URL', 'https://remarkableapp.github.io/')
cdata.set('VERSION', version)
cdata.set('PY_LIB_LOC', '"@0@"'.format(pylib_loc))
cdata.set('PY_ABI_FLAGS', '"@0@"'.format(python_abi_flags))
cdata.set('PY_LIB_SUFFIX', '"@0@"'.format(pylib_suffix))
cdata.set('PYTHON_VERSION', '"@0@"'.format(python_dep.version()))


message('Python Directory is :' + python_dir)
message('Preparing init file')
configure_file(input : 'remarkable.in', output : 'remarkable', configuration : cdata, install_dir : 'bin')
message('generated binary')

