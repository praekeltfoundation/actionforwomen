#!/bin/bash

cp -a $REPO ./build/

# ensure `praekelt-pyramid-celery` is removed from sideloader workspace

${PIP} install -r $REPO/requirements.txt -U
