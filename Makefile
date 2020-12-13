SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	mypy octadocs tests/**/*.py
	flake8 .
	doc8 -q docs

.PHONY: unit
unit:
	pytest

.PHONY: package
package:
	poetry check
	pip check
	# Ignoring sphinx@2 security issue for now, see:
  # https://github.com/miyakogi/m2r/issues/51
	safety check --full-report -i 38330

.PHONY: test
test: lint package unit

docs/rdfs/class/classes.svg: docs/rdfs/class/classes.drawio
	drawio --export docs/rdfs/class/classes.drawio --output docs/rdfs/class/classes.svg --transparent

docs/schema.n3:
	curl -s https://schema.org/version/latest/schemaorg-current-http.ttl | gunzip > docs/schema.n3

update: docs/rdfs/class/classes.svg docs/schema.n3
