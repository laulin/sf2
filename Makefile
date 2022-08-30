build :
	python3 setup.py sdist bdist_wheel

upload:
	twine upload dist/*

compile:
	pyinstaller -n sf2-1.4.0-cli -F bin/cli.py -p .
	pyinstaller -n sf2-1.4.0-gui -F bin/gui.py -p .

clean:
	rm -f *.spec
	rm -rf build/ dist/

tests:
	python3 -m unittest discover -s test