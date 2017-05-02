version = '1.87'


message('Getting python directiories')

py3_mod = import('python3')
py3 = py3_mod.find_python()

py3_version = py3_mod.language_version()
if py3_version.version_compare('< 3.2')
  error('Invalid python version!?')
endif

py3_purelib = py3_mod.sysconfig_path('purelib')
if not py3_purelib.endswith('site-packages')
  error('Python3 purelib path seems invalid?')
endif

message('Python version installed : ' + py3_version)
message('Python library path : ' + py3_purelib)
pythonlibpath=join_paths(get_option('prefix'),py3_purelib)
message('is this it??? ' + pythonlibpath)
# Configuration params

cdata = configuration_data()
cdata.set('PACKAGE', '"Remarkable"')
# Configuration params
cdata.set('PACKAGE_URL', 'https://remarkableapp.github.io/')
cdata.set('VERSION', version)
cdata.set('PYTHON_LIB_PATH', py3_purelib)


message('Preparing init file')
configure_file(input : 'remarkable.in', output : 'remarkable', configuration : cdata, install_dir : 'bin')
message('generated binary')

