all:

test:
	python3 -m pytest \
	    --cov=hpargparse \
	    --no-cov-on-fail \
	    --cov-report=html:test-results/htmlcov \
	    --cov-report term \
	    --doctest-modules \
	    hpargparse tests

style-check:
	black --diff --check .

serve-coverage-report:
	cd test-results/htmlcov && python3 -m http.server

wheel:
	python3 setup.py sdist bdist_wheel

doc:
	cd docs && ./gendoc.sh

install:  
	# install prerequisites
	# TODO: 
	#   1. install requirments
	#   2. install pre-commit hook
	
