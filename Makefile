build :
	python3 -m build

upload:
	twine updoad dist/*

compile:
	pyinstaller -n sf2-1.3.0-cli -F bin/cli.py -p .
	pyinstaller -n sf2-1.3.0-gui -F bin/gui.py -p .