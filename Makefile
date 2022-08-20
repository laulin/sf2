build :
	python3 -m build

upload:
	twine updoad dist/*

compile:
	pyinstaller -n sf2-1.2.0 -F bin/main.py