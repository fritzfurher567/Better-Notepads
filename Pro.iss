[Setup]
AppId={{B6E1B1B0-1A11-4D2E-9C1A-A1A1A1A10003}
AppName=Notepad Pro
AppVersion=1.0
AppPublisher=Fritz
DefaultDirName={autopf}\NotepadPro
DefaultGroupName=Notepad Pro
DisableProgramGroupPage=yes
OutputDir=dist-installers
OutputBaseFilename=NotepadPro-Setup
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\Notepad-Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Notepad Pro"; Filename: "{app}\Notepad-Pro.exe"
Name: "{group}\Uninstall Notepad Pro"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Notepad Pro"; Filename: "{app}\Notepad-Pro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Notepad-Pro.exe"; Description: "Launch Notepad Pro"; Flags: nowait postinstall skipifsilent
