#!/bin/sh

set -e

test -n "$srcdir" || srcdir=$1
test -n "$srcdir" || srcdir=.

cd $srcdir

VERSION=$(git describe --abbrev=0)
NAME="remarkable-$VERSION"

echo "Creating git tree archive…"
git archive --prefix="${NAME}/" --format=tar HEAD > remarkable.tar


cd ../..

rm -f "${NAME}.tar"

tar -Af "${NAME}.tar" remarkable.tar

rm -f nautilus.tar

echo "Compressing archive…"
xz --verbose -f "${NAME}.tar"
