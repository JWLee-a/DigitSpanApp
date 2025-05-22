[Setup]
AppName=DigitSpan Test
AppVersion=1.0
DefaultDirName={pf}\DigitSpanTest
DefaultGroupName=DigitSpan Test
OutputDir=dist
OutputBaseFilename=DigitSpanSetup
SetupIconFile=digitham.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\ishik\PycharmProjects\DigitSpanApp\Win_v1\DigitSpanApp\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DigitSpan Test"; Filename: "{app}\main.exe"
Name: "{commondesktop}\DigitSpan Test"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
