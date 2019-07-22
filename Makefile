TAG := $(shell git rev-parse --short HEAD)
DIR := $(shell pwd -L)


build:
	python3 setup.py bdist_wheel

run:
	./pkg/scripts/verify_package_installers
	./pkg/station-check/station_check.py

deploy: build
	python3 -m twine upload dist/*

clean:
	rm -rf build/
	rm -rf dist/
