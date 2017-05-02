version = '1.87'

# Configuration params
conf = configuration_data()
conf.set('PACKAGE_VERSION', version)
conf.set('PACKAGE_URL', 'https://remarkableapp.github.io/')

message('Getting python install dir')
r = run_command(py3, '-c', 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')
if r.returncode() != 0
    error('Cannot find python install dir')
endif
python_dir = r.stdout().strip()
conf.set('PYTHONDIR', 'python_dir')
message('Python Directory is :' + python_dir)
message('Preparing init file')
configure_file(input : 'remarkable.in', output : 'remarkable', configuration : conf, install_dir : 'bin')
message('generated binary')

