@echo off
set ZIP=C:\PROGRA~1\7-Zip\7z.exe a -tzip -y -r
set REPO=hoochie_mama
set PACKID=1460733408
set VERSION=0.4.1

echo %VERSION% >%REPO%\VERSION

fsum -r -jm -md5 -d%REPO% * > checksum.md5
move checksum.md5 %REPO%\checksum.md5

%ZIP% %REPO%_v%VERSION%_Anki20.zip *.py %REPO%\*
cd %REPO%

quick_manifest.exe "Hoochie Mama: RevQ" "%PACKID%" >manifest.json
%ZIP% ../%REPO%_v%VERSION%_Anki21.ankiaddon *

quick_manifest.exe "Hoochie Mama: RevQ" "%REPO%" >manifest.json
%ZIP% ../%REPO%_v%VERSION%_CCBC.adze *
