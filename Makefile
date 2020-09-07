.PHONY: deps build install clean clean_env clean_all

SITE_PACKAGES=.env/lib/python3.6/site-packages/
IN_ENV=source .env/bin/activate;

default: .env deps build

.env:
	@python3 -m venv .env

deps:
	@pip install -U pip
	@pip install -r requirements.txt

build:
	@${IN_ENV} mkdir -p build && ansible-galaxy collection build -vvvv -f --output-path build

install: build
	@${IN_ENV} ansible-galaxy collection install -vvvv -f build/*.tar.gz

clean:
	@rm -rf build

clean_env:
	@rm -rf .env

clean_all: clean clean_env
