#!/bin/bash
killall tor
mkdir -p ${DOWNLOAD_DIR}
echo $VERSION_ARCH
echo ${TBB_ARCHIVE_URL}/${VERSION_ARCH}
[ ! -e ${DOWNLOAD_DIR}/$TARBALL ] && wget -P ${DOWNLOAD_DIR} ${TBB_ARCHIVE_URL}/${VERSION_ARCH}
tar -xf ${DOWNLOAD_DIR}/$TARBALL -C $HOME
