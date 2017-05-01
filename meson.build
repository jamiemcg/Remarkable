project('remarkable', 'c')

version = '1.87'

# Configuration params
conf = configuration_data()
conf.set('PACKAGE_VERSION', version)
conf.set('PACKAGE_URL', 'https://remarkableapp.github.io/')

message('Looking for dependencies')
py3 = find_program('python3')
glib = dependency('glib-2.0')
gobject = dependency('gobject-2.0')
gir = dependency('gobject-introspection-1.0')
gtk = dependency('gtk+-3.0', version : '>=3.13.2')

message('Getting python install dir')
r = run_command(py3, '-c', 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')
if r.returncode() != 0
    error('Cannot find python install dir')
endif
python_dir = r.stdout().strip()

subdir('data/glib-2.0/schemas')
subdir('data/media')
subdir('data')
subdir('bin')

message('Install source code medata')
install_data('LICENSE', install_dir : 'share/doc/remarkable')
install_data('README.md', install_dir : 'share/doc/remarkable')

message('Installing Python files')
install_subdir('markdown/extensions', install_dir: python_dir)
install_subdir('pdfkit', install_dir: python_dir)
install_subdir('remarkable', install_dir: python_dir)
install_subdir('remarkable_lib', install_dir: python_dir)

message('Installing .desktop file')
install_data('remarkable.desktop', install_dir : 'share/applications')

meson.add_install_script('meson_install.sh')
