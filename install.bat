@echo off
chcp 65001 >nul
setlocal EnableExtensions

cd /d "%~dp0"

set "APP_NAME=古埃及文字翻译器"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\EgyptChineseTranslator"
set "GUI_FILE=%CD%\gui.py"
set "DICT_FILE=%CD%\dictionary.json"
set "ICON_PNG=%CD%\中国.png"
set "ICON_ICO=%CD%\中国.ico"

 echo.
 echo ================================================
 echo   Установка %APP_NAME%
 echo ================================================
 echo.

rem Проверяем обязательные файлы.
if not exist "%GUI_FILE%" (
    echo [ОШИБКА] Рядом с батником не найден gui.py
    goto :fail
)
if not exist "%DICT_FILE%" (
    echo [ОШИБКА] Рядом с батником не найден dictionary.json
    goto :fail
)
if not exist "%ICON_PNG%" (
    echo [ОШИБКА] Рядом с батником не найден 中国.png
    goto :fail
)

rem Ищем Python Launcher или обычный python.exe.
where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo [ОШИБКА] Python не найден.
        echo Установи Python 3 и включи опцию Add Python to PATH.
        goto :fail
    )
    set "PY=python"
)

echo [1/5] Обновление pip...
%PY% -m pip install --upgrade pip
if errorlevel 1 goto :python_fail

echo.
echo [2/5] Установка Pillow и PyInstaller...
%PY% -m pip install --upgrade pillow pyinstaller
if errorlevel 1 goto :python_fail

echo.
echo [3/5] Создание Windows-иконки из 中国.png...
%PY% -c "from PIL import Image; import os; src=os.environ['ICON_PNG']; dst=os.environ['ICON_ICO']; Image.open(src).convert('RGBA').save(dst, format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
if errorlevel 1 goto :python_fail

echo.
echo [4/5] Сборка приложения...
%PY% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --noconsole ^
    --name "%APP_NAME%" ^
    --icon "%ICON_ICO%" ^
    --add-data "%DICT_FILE%;." ^
    --add-data "%ICON_PNG%;." ^
    "%GUI_FILE%"
if errorlevel 1 goto :python_fail

set "BUILT_EXE=%CD%\dist\%APP_NAME%.exe"
if not exist "%BUILT_EXE%" (
    echo [ОШИБКА] PyInstaller завершился, но EXE не найден.
    goto :fail
)

echo.
echo [5/5] Установка и создание ярлыка...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if errorlevel 1 goto :fail

copy /Y "%BUILT_EXE%" "%INSTALL_DIR%\%APP_NAME%.exe" >nul
if errorlevel 1 goto :fail

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$desktop=[Environment]::GetFolderPath('Desktop');" ^
  "$target=Join-Path $env:INSTALL_DIR ($env:APP_NAME + '.exe');" ^
  "$shortcut=Join-Path $desktop ($env:APP_NAME + '.lnk');" ^
  "$shell=New-Object -ComObject WScript.Shell;" ^
  "$link=$shell.CreateShortcut($shortcut);" ^
  "$link.TargetPath=$target;" ^
  "$link.WorkingDirectory=$env:INSTALL_DIR;" ^
  "$link.IconLocation=$target + ',0';" ^
  "$link.Description='Переводчик древнеегипетского и упрощённого китайского';" ^
  "$link.Save();"
if errorlevel 1 goto :fail

rem Удаляем только временную папку сборки и spec-файл. EXE в dist остаётся.
if exist "%CD%\build" rmdir /S /Q "%CD%\build"
if exist "%CD%\%APP_NAME%.spec" del /Q "%CD%\%APP_NAME%.spec"

echo.
echo ================================================
echo   Готово!
echo ================================================
echo Приложение установлено сюда:
echo %INSTALL_DIR%\%APP_NAME%.exe
echo.
echo Ярлык создан на рабочем столе.
echo.
pause
exit /b 0

:python_fail
echo.
echo [ОШИБКА] Команда Python завершилась с ошибкой.
echo Посмотри текст ошибки выше.
goto :fail

:fail
echo.
echo Установка не завершена.
pause
exit /b 1
