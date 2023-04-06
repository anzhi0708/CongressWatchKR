all:
	python3 setup.py sdist bdist_wheel
install:
	python3 setup.py sdist bdist_wheel
	python3 -m pip install dist/*.tar.gz
uninstall:
	python3 -m pip uninstall dearaj -y
	python3 -m pip cache purge
	rm -rf src/dearaj/__pycache__ dist build src/dearaj.egg-info
commit:
	git commit -a
	git push -u origin main
format:
	black src/dearaj/*.py
	mypy src/dearaj/*.py
clean:
	rm -rf src/dearaj/__pycache__ dist build src/dearaj.egg-info
