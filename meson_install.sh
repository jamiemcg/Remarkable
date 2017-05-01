#!/bin/sh

# Update icon caches
#gtk-update-icon-cache -f -t ${DESTDIR}/${MESON_INSTALL_PREFIX}/share/icons/hicolor
#gtk-update-icon-cache -f -t ${DESTDIR}/${MESON_INSTALL_PREFIX}/share/icons/HighContrast

# Install new schemas
glib-compile-schemas ${DESTDIR}/${MESON_INSTALL_PREFIX}/share/glib-2.0/schemas/
