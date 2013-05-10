; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "ClipManager"
#define MyAppVersion "0.1"
#define MyAppPublisher "Werner"
#define MyAppURL "scott.werner.vt@gmail.com"
#define MyAppExeName "clipmanager.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{2D71377F-AF64-4DB3-BD1E-0597F1FB3DFB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=clipmanager\license.txt
OutputDir=dist
OutputBaseFilename=clipmanager-setup-0.2
SetupIconFile=clipmanager\icons\app.ico
Compression=lzma
SolidCompression=yes
; http://www.jrsoftware.org/iskb.php?startup
PrivilegesRequired=admin
; http://www.jrsoftware.org/iskb.php?mutexsessions
AppMutex=Werner.ClipManager,Global\Werner.ClipManager
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "build\exe.win32-2.7\clipmanager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win32-2.7\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; AppUserModelID: "{#MyAppPublisher}.{#MyAppName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; AppUserModelID: "{#MyAppPublisher}.{#MyAppName}"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; AppUserModelID: "{#MyAppPublisher}.{#MyAppName}"
; http://www.jrsoftware.org/iskb.php?startup
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; AppUserModelID: "{#MyAppPublisher}.{#MyAppName}"; Flags:

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{commonstartup}\{#MyAppName}"
