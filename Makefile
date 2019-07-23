TAG := $(shell git rev-parse --short HEAD)
DIR := $(shell pwd -L)

dep:
	pipenv install --system

lint:
	docker run -ti \
        --mount src="$(DIR)",target="/go/src/$(PROJECT_PATH)",type="bind" \
        -w "/go/src/$(PROJECT_PATH)" \
        registry.hub.docker.com/asecurityteam/sdcli:v1 python lint
test:
	pytest

build:
	python3 setup.py bdist_wheel

run:
	./stationcheck

deploy: build
	python3 -m twine upload dist/*

clean:
	rm -rf build/
	rm -rf dist/
