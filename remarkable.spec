Summary:	Markdown editor
Name:		remarkable
Version:	1.87
Release:	1

Source:		https://github.com/jamiemcg/Remarkable/archive/remarkable-%{version}.tar.xz
Packager:	uraeus@gnome.org
License:	MIT
Group:		Applications/Productivity
URL:		https://remarkableapp.github.io/
BuildRoot:      %{_tmppath}/remarkable-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	python3
BuildRequires: python3-devel
BuildRequires: meson

BuildArch: 	noarch

%description
Remarkable markdown editor application. Allows you to edit in Markdown format for use with Wikis.

%prep
%autosetup

%build

%meson
%meson_build
desktop-file-validate remarkable.desktop
%meson_install

%post
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%{_bindir}/remarkable
%{python3_sitelib}/remarkable
%{python3_sitelib}/remarkable_lib
%{python3_sitelib}/markdown/extensions
%{python3_sitelib}/pdfkit
%{_datadir}/glib-2.0/schemas
%{_datadir}/remarkable/ui
%{_datadir}/icons/hicolor/256x256/apps/remarkable.png
%{_datadir}/icons/hicolor/scaleable/apps/remarkable.svg
%{_datadir}/remarkable/media/MarkdownTutorial.md
%{_datadir}/appdata/remarkable.appdata.xml
%{_datadir}/applications/remarkable.desktop

%changelog
*  Thu Apr 27 2017 Christian F.K. Schaller <uraeus@gnome.org>
- Initial release
