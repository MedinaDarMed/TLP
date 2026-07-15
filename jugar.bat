@echo off
REM --- Script para compilar y ejecutar juegos de BrickScript ---

REM Limpia la pantalla para una ejecucion limpia
cls

REM Verifica si se proporciono un nombre de juego.
if "%1"=="" (
    echo.
    echo  Uso: jugar [nombre_del_juego]
    echo  Ejemplo: jugar snake_evolved
    echo  Ejemplo: jugar tetris_remake
    echo  Ejemplo: jugar brick_tanks
    echo.
    goto :eof
)

REM --- DETECCION DE PYTHON ---
REM Prioridad: 1) py -2 (Python Launcher, forzando Python 2.7)
REM            2) python (si "python" del PATH ya es 2.7)
REM            3) C:\Python27\python.exe (ruta fija de respaldo)
set PYTHON_EXE=
py -2 -c "1" >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_EXE=py -2
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_EXE=python
    ) else (
        if exist C:\Python27\python.exe (
            set PYTHON_EXE=C:\Python27\python.exe
        ) else (
            echo !!! Error: No se encontro Python 2.7 ^(ni "py -2", ni "python", ni C:\Python27^) !!!
            pause
            goto :eof
        )
    )
)

REM --- FASE 1: COMPILACION ---
echo Compilando el juego: %1...
echo ----------------------------------

REM Ejecuta el compilador de Python (usa el interprete detectado arriba).
%PYTHON_EXE% .\compiler.py .\games\%1.brick

REM Verifica si el comando anterior (la compilacion) fallo.
if errorlevel 1 (
    echo.
    echo !!! Ocurrio un error durante la compilacion. !!!
    echo Revisa los mensajes de error de arriba.
    pause
    goto :eof
)

echo.
echo Compilacion exitosa. Iniciando el juego...
echo ----------------------------------
REM Se elimina la pausa para iniciar la GUI inmediatamente

REM --- FASE 2: EJECUCION ---
REM Ejecuta el motor del juego (runtime.py modificado con GUI).
%PYTHON_EXE% .\runtime.py .\games\%1.json

REM Fin del script.
echo.
echo El juego se ha cerrado. Presiona cualquier tecla para cerrar esta ventana.
pause
