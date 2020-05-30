all:

test:
	mkdir -p test-results
	python3 -m pytest \
	    --cov=hpargparse \
	    --no-cov-on-fail \
	    --cov-report=html:test-results/htmlcov \
	    --cov-report term \
	    --doctest-modules \
	    --junitxml=test-results/junit.xml \
	    hpargparse tests
	python3 -m coverage xml -o test-results/coverage.xml

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
	
