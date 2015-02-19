.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "fake_deploy - copy files to local site-packages"

clean: clean-build clean-pyc

fake_deploy:
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/provider.pyc
	rm /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/models.pyc
	rm /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/cloudstack_bundle.pyc
	rm /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/cloudstack_pack.pyc
	rm /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/cloudstack_region.pyc
	rm /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/cloudstack_serviceoffering.pyc
	cp dbaas_cloudstack/provider.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/
	cp dbaas_cloudstack/models.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/
	cp dbaas_cloudstack/admin/cloudstack_bundle.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/
	cp dbaas_cloudstack/admin/cloudstack_pack.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/
	cp dbaas_cloudstack/admin/cloudstack_region.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/
	cp dbaas_cloudstack/admin/cloudstack_serviceoffering.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_cloudstack/admin/


clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 dbaas-cloudstack tests

test:
	python runtests.py test

test-all:
	tox

coverage:
	coverage run --source dbaas-cloudstack setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/dbaas-cloudstack.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ dbaas-cloudstack
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release:
	python setup.py sdist upload

release_globo:
	python setup.py sdist upload -r ipypiglobo

sdist: clean
	python setup.py sdist
	ls -l dist
