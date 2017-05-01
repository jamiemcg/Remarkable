Summary:	Markdown editor
Name:		Remarkable
Version:	1.87
Release:	1

Source:		https://github.com/jamiemcg/Remarkable/archive/remarkable-1.87-1-gf9ebac5.tar.xz
Packager:	uraeus@gnome.org
License:	MIT
Group:		Applications/Productivity
URL:		https://remarkableapp.github.io/
BuildRoot:      %{_tmppath}/remarkable-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	python3

BuildArch: 	noarch

%description
Remarkable markdown editor application. Allows you to edit in Markdown format for use with Wikis.

%prep
%setup

%install

xz -d remarkable-1.87-1-gf9ebac5.tar.xz
tar -xvf remarkable-1.87-1-gf9ebac5.tar
cd remarkable-1.87-1-gf9ebac5
meson install

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
