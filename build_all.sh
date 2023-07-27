#!/bin/bash

usage()
{
   echo "Usage: $0 -r [REGISTRY URL]"
   echo "   -r aaa.dkr.ecr.us-east-2.amazonaws.com/bbb will build and push"
   echo "  ./environment/foo/Dockerfile to aaa.dkr.ecr.us-east-2.amazonaws.com/bbb/foo:tag"
   exit 1
}
if [[ ${#} -eq 0 ]]; then
   usage
fi
while getopts "r:" opt
do
   case "$opt" in
      r ) registry="$OPTARG" ;;
      ? ) usage ;;
   esac
done
ENVIRONMENTS_PATH="./environments"

# Build our base image / parent image. All of the other images will derive this one
PARENT_IMAGE=$(astro dev parse 2>&1 | tee /dev/tty | sed -nr 's/.+naming to docker.io\/(.+):latest[ ].+/\1/p')

set -euxo pipefail
for environment in $(ls $ENVIRONMENTS_PATH) ; do
   pushd $ENVIRONMENTS_PATH/${environment}
   docker build -t ${registry}/${PARENT_IMAGE}/${environment} --build-arg="BASE_IMAGE=${PARENT_IMAGE}"  .
   docker push ${registry}/${PARENT_IMAGE}/${environment}
   popd
done