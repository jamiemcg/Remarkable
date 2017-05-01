#!/bin/sh

set -e

test -n "$srcdir" || srcdir=$1
test -n "$srcdir" || srcdir=.
echo 'Done testing for src dir'

cd $srcdir

echo 'Getting version number from git'
VERSION=$(git describe --tags)
echo 'Setting name'
NAME="remarkable-${VERSION}"

echo "Creating git tree archive…"
git archive --prefix="${NAME}/" --format=tar HEAD > remarkable-${VERSION}.tar

echo "Compressing archive…"
xz --verbose -f "${NAME}.tar"
