[Setup]
AppId={{B6E1B1B0-1A11-4D2E-9C1A-A1A1A1A10002}
AppName=Notepad Standard
AppVersion=1.0
AppPublisher=Fritz
DefaultDirName={autopf}\NotepadStandard
DefaultGroupName=Notepad Standard
DisableProgramGroupPage=yes
OutputDir=..\dist-installers
OutputBaseFilename=NotepadStandard-Setup
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
Source: "..\dist\Notepad-Standard.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Notepad Standard"; Filename: "{app}\Notepad-Standard.exe"
Name: "{group}\Uninstall Notepad Standard"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Notepad Standard"; Filename: "{app}\Notepad-Standard.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Notepad-Standard.exe"; Description: "Launch Notepad Standard"; Flags: nowait postinstall skipifsilent
