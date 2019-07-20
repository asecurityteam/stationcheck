TAG := $(shell git rev-parse --short HEAD)
DIR := $(shell pwd -L)
GOPATH := ${GOPATH}
ifeq ($(GOPATH),)
	GOPATH := ${HOME}/go
endif
PROJECT_PATH := $(subst $(GOPATH)/src/,,$(DIR))

run:
	python3 pkg/secdev-station-check/station_check.py

deploy: ;
