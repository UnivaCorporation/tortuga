#!/bin/bash
DOCKER_TAG="${DOCKER_TAG:-$TRAVIS_BUILD_NUMBER}"

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker tag univa/tortuga-build-kit:$DOCKER_TAG univa/tortuga-build-kit:$TRAVIS_BRANCH-latest
docker push univa/tortuga-build-kit:$DOCKER_TAG
docker push univa/tortuga-build-kit:$TRAVIS_BRANCH-latest
