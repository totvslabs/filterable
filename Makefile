publish:
	python setup.py sdist
	twine upload dist/*
	rm -rf filterable.egg-info
	rm -rf dist