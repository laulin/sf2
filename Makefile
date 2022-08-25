build :
	python3 setup.py sdist bdist_wheel

upload:
	twine updoad dist/*

compile:
	pyinstaller -n sf2-1.4.0-cli -F bin/cli.py -p .
	pyinstaller -n sf2-1.4.0-gui -F bin/gui.py -p .