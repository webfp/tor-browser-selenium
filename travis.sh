#!/bin/bash
tarball=`echo ${VERSION_ARCH} |cut -d'/' -f 2`
locale=`echo $tarball |cut -d'_' -f 2 | cut -d'.' -f 1`
mkdir -p ${DOWNLOAD_DIR}
[ ! -e ${DOWNLOAD_DIR}/$tarball ] && wget -P ${DOWNLOAD_DIR} ${TBB_ARCHIVE_URL}/${VERSION_ARCH}
tar -xf ${DOWNLOAD_DIR}/$tarball -C $HOME
TBB_PATH=${HOME}/tor-browser_$locale
