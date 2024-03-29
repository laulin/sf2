build :
	python3 setup.py sdist bdist_wheel

upload:
	twine upload dist/*

compile:
	pyinstaller -n sf2-2.0.0-cli -F bin/cli.py -p .

clean:
	rm -f *.spec
	rm -rf build/ dist/

tests:
	python3 -m unittest discover -s test -p test_*.py

integration:
	python3 -m unittest discover -s test -p int_*.py

docker:
	docker build -t test_sf2 .