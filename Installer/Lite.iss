[Setup]
AppId={{B6E1B1B0-1A11-4D2E-9C1A-A1A1A1A10001}
AppName=Notepad Lite
AppVersion=1.0
AppPublisher=Fritz
DefaultDirName={autopf}\NotepadLite
DefaultGroupName=Notepad Lite
DisableProgramGroupPage=yes
OutputDir=..\dist-installers
OutputBaseFilename=NotepadLite-Setup
Compression=lzma
SolidCompression=yes
LicenseFile=..\LICENSE
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\Notepad-Lite.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Notepad Lite"; Filename: "{app}\Notepad-Lite.exe"
Name: "{group}\Uninstall Notepad Lite"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Notepad Lite"; Filename: "{app}\Notepad-Lite.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Notepad-Lite.exe"; Description: "Launch Notepad Lite"; Flags: nowait postinstall skipifsilent
