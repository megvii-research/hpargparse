all:

test:
	pytest \
	    --cov=hpargparse \
	    --no-cov-on-fail \
	    --cov-report=html:htmlcov \
	    --cov-report term \
	    --doctest-modules \
	    hpargparse tests

serve-coverage-report:
	cd htmlcov && python3 -m http.server

doc:
	# TODO
	
install:  
	# install prerequisites
	# TODO: 
	#   1. install requirments
	#   2. install pre-commit hook
	
