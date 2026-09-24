[Setup]
AppName=Intel Optimizer UI
AppVersion=1.0
DefaultDirName={autopf}\Intel Optimizer UI
DefaultGroupName=Intel Optimizer UI
OutputDir=Output
OutputBaseFilename=IntelOptimizerUI_Setup
SetupIconFile=image\icon_app.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "IntelOptimizerUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "image\icon_app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Intel Optimizer UI"; Filename: "{app}\IntelOptimizerUI.exe"; IconFilename: "{app}\icon_app.ico"
Name: "{autodesktop}\Intel Optimizer UI"; Filename: "{app}\IntelOptimizerUI.exe"; IconFilename: "{app}\icon_app.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\IntelOptimizerUI.exe"; Description: "{cm:LaunchProgram,Intel Optimizer UI}"; Flags: nowait postinstall skipifsilent
