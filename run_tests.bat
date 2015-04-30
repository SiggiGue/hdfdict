@echo off
set testenv=
set testenv="testingenv"
set testdir=
set testdir="tests/"
set curdir=
set curdir="%CD%\"
@echo.
@echo.
@echo ============================== Run Tests =====================================
@echo Date:
call date /t
@echo Time:
call time /t
@echo.
@echo off
set pkg=
for /F %%i in ("%CD%") do (
set pkg=%%~ni
)
call activate %testenv%
@echo.
@echo Uninstall the package if necessary:
pip uninstall %pkg% -y
pip uninstall -r requirements.txt -y
@echo.
@echo Install the package:
pip install .
pip install -r requirements.txt
@echo.
cd %testdir%
py.test -v
@echo.
pip uninstall %pkg% -y
cd %curdir%
pip uninstall -r requirements.txt -y
@echo.
call deactivate

@echo.
@echo ======== Finished Tests: Please check the test session results above =========
@echo off
