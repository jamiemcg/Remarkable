#!/bin/sh

set -e

test -n "$srcdir" || srcdir=$1
test -n "$srcdir" || srcdir=.
echo 'Done testing for src dir'

cd $srcdir

echo 'Getting version number from git'
VERSION=$(git describe --abbrev=0)
echo 'Setting name'
NAME="remarkable-$VERSION"

echo "Creating git tree archive…"
git archive --prefix="${NAME}/" --format=tar HEAD > remarkable.tar


cd ../..

rm -f "${NAME}.tar"

tar -Af "${NAME}.tar" remarkable.tar

rm -f nautilus.tar

echo "Compressing archive…"
xz --verbose -f "${NAME}.tar"
