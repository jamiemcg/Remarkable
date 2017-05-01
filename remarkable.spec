Summary:	Markdown editor
Name:		Remarkable
Version:	1.87
Release:	1

Source:		https://github.com/jamiemcg/Remarkable/archive/Remarkable-1.87.zip
Packager:	uraeus@gnome.org
License:	MIT
Group:		Applications/Productivity
URL:		https://remarkableapp.github.io/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	python3

BuildArch: 	noarch

%description
Remarkable markdown editor application. Allows you to edit in Markdown format for use with Wikis.

%prep
%setup -q Remarkable

# %build

%install
mkdir -p %{buildroot}
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}/
mkdir -p $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
mkdir -p $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
mkdir -p $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
mkdir -p $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scaleable/apps/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/remarkable/ui
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata/


cp bin/remarkable $RPM_BUILD_ROOT%{_bindir}
cp markdown/extensions/Highlighting.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/Strikethrough.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/markdown_checklist.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/mathjax.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/subscript.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/superscript.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp markdown/extensions/urlize.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/markdown/extensions
cp pdfkit/__init__.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
cp pdfkit/api.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
cp pdfkit/configuration.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
cp pdfkit/pdfkit.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
cp pdfkit/source.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/pdfkit
cp remarkable/AboutRemarkableDialog.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable/RemarkableWindow.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable/__init__.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable/configuration.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable/styles.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable/undobuffer.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable
cp remarkable_lib/AboutDialog.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp remarkable_lib/Builder.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp remarkable_lib/Window.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp remarkable_lib/__init__.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp remarkable_lib/helpers.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp remarkable_lib/remarkableconfig.py $RPM_BUILD_ROOT%{_libdir}/python3/dist-packages/remarkable_lib
cp data/media/remarkable.svg $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scaleable/apps/remarkable.svg
cp data/ui/* $RPM_BUILD_ROOT%{_datadir}/remarkable/ui
cp remarkable.desktop $RPM_BUILD_ROOT/%{_datadir}/applications
cp remarkable.appdata.xml $RPM_BUILD_ROOT%{_datadir}/appdata


desktop-file-validate remarkable.desktop

%post
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc 
%{_bindir}/remarkable
%{_libdir}/python3/dist-packages/markdown/extensions
%{_libdir}/python3/dist-packages/pdfkit
%{_libdir}/python3/dist-packages/remarkable
%{_libdir}/python3/dist-packages/remarkable_lib
%{_datadir}/remarkable/ui/*.*
%{_datadir}/icons/hicolor/scaleable/apps/remarkable.svg
%{_datadir}/appdata/remarkable.appdata.xml
%{_datadir}/applications/remarkable.desktop

%changelog
*  Thu Apr 27 2017 Christian F.K. Schaller <uraeus@gnome.org>
- Initial release
