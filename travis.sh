#!/bin/bash
killall tor
mkdir -p ${DOWNLOAD_DIR}
echo $VERSION_ARCH
echo ${TBB_DIST_URL}/${VERSION_ARCH}
[ ! -e ${DOWNLOAD_DIR}/$TARBALL ] && wget -P ${DOWNLOAD_DIR} ${TBB_DIST_URL}/${VERSION_ARCH}
tar -xf ${DOWNLOAD_DIR}/$TARBALL -C $HOME
echo `which curl`

# v0.17 works well with ESR 52.
geckodriver_url="https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz"
geckodriver_tarball=`basename ${geckodriver_url}`
echo $geckodriver_tarball
wget -P ${DOWNLOAD_DIR} $geckodriver_url
tar -xf ${DOWNLOAD_DIR}/$geckodriver_tarball -C $HOME
export PATH=$PATH:$HOME
