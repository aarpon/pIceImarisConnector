@ECHO OFF
if exist build rd /s /q build
rd /s /q dist
python setup.py bdist_wheel
rd /s /q build
dir dist
