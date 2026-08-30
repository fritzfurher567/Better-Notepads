[Setup]
AppId={{B6E1B1B0-1A11-4D2E-9C1A-A1A1A1A19999}
AppName=Better Notepads
AppVersion=2.0
AppPublisher=Fritz
DefaultDirName={autopf}\BetterNotepads
DefaultGroupName=Better Notepads
DisableProgramGroupPage=yes
OutputDir=..\dist-installers
OutputBaseFilename=BetterNotepads-Setup
Compression=lzma
SolidCompression=yes
LicenseFile=..\LICENSE
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ---- lets the wizard show a "which edition?" selection page ----
[Types]
Name: "lite"; Description: "Notepad Lite - minimal and fast"
Name: "standard"; Description: "Notepad Standard - tabs, formatting toolbar, full features"
Name: "pro"; Description: "Notepad Pro - Standard + recent files, autosave, syntax highlighting, themes"
Name: "custom"; Description: "Custom (choose more than one)"; Flags: iscustom

[Components]
Name: "lite"; Description: "Notepad Lite"; Types: lite custom
Name: "standard"; Description: "Notepad Standard"; Types: standard custom
Name: "pro"; Description: "Notepad Pro"; Types: pro custom

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\Notepad-Lite.exe"; DestDir: "{app}"; Components: lite; Flags: ignoreversion
Source: "..\dist\Notepad-Standard.exe"; DestDir: "{app}"; Components: standard; Flags: ignoreversion
Source: "..\dist\Notepad-Pro.exe"; DestDir: "{app}"; Components: pro; Flags: ignoreversion

[Icons]
Name: "{group}\Notepad Lite"; Filename: "{app}\Notepad-Lite.exe"; Components: lite
Name: "{group}\Notepad Standard"; Filename: "{app}\Notepad-Standard.exe"; Components: standard
Name: "{group}\Notepad Pro"; Filename: "{app}\Notepad-Pro.exe"; Components: pro
Name: "{group}\Uninstall Better Notepads"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Notepad Lite"; Filename: "{app}\Notepad-Lite.exe"; Components: lite; Tasks: desktopicon
Name: "{autodesktop}\Notepad Standard"; Filename: "{app}\Notepad-Standard.exe"; Components: standard; Tasks: desktopicon
Name: "{autodesktop}\Notepad Pro"; Filename: "{app}\Notepad-Pro.exe"; Components: pro; Tasks: desktopicon

[Run]
Filename: "{app}\Notepad-Lite.exe"; Description: "Launch Notepad Lite"; Flags: nowait postinstall skipifsilent unchecked; Components: lite
Filename: "{app}\Notepad-Standard.exe"; Description: "Launch Notepad Standard"; Flags: nowait postinstall skipifsilent unchecked; Components: standard
Filename: "{app}\Notepad-Pro.exe"; Description: "Launch Notepad Pro"; Flags: nowait postinstall skipifsilent unchecked; Components: pro
