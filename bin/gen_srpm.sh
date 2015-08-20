#!/bin/bash

# Generate srpm using remote build server

set -e
set -x

APP_NAME=$1
VERSION=$2
BUILD_SERVER=$3
SPECFILEBODY=$4
APP="$APP_NAME-$VERSION"
SPECFILE=${APP_NAME}.spec

# Write spec file
mkdir -p dist
echo "%define version $VERSION" > dist/$SPECFILE
cat $SPECFILEBODY >> dist/$SPECFILE

# Create source distribution
python setup.py sdist

# prepare rpmbuild area
rm -rf dist/rpmbuild
mkdir -p dist/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
mv dist/$APP.tar.gz dist/rpmbuild/SOURCES
mv dist/$SPECFILE dist/rpmbuild/SPECS

# prepare remote rpmbuild area
ssh $BUILD_SERVER "rm -rf build/$APP && mkdir -p build/$APP"

# copy rpmbuild area
cd dist; tar cf - rpmbuild | ssh $BUILD_SERVER "tar xf - -C build/$APP"

# build SRPM on remote machine
ssh $BUILD_SERVER << EOF
    cd build/$APP/rpmbuild
    rpmbuild --define "_topdir \`pwd\`" -bs SPECS/$SPECFILE
EOF
scp $BUILD_SERVER:build/$APP/rpmbuild/SRPMS/* .

