; setup.iss
#define MyAppName "Rodam"
; A versão será injetada via linha de comando pelo GitHub Actions
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0" 
#endif
#define MyAppPublisher "Seu Nome ou Empresa"
#define MyAppExeName "Rodam.exe"

[Setup]
; Identificador único (gere um novo GUID no Inno Setup ou online para seu app)
AppId={{D45A66B1-1234-4567-8901-MYAPPID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; Cria o desinstalador
UninstallDisplayIcon={app}\{#MyAppExeName}
; Onde o instalador final será salvo (pasta dist)
OutputDir=dist
OutputBaseFilename=Rodam-Setup-Windows-{#MyAppVersion}
; Ícone do instalador (opcional, coloque um .ico na raiz ou remova a linha)
SetupIconFile=resources\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Pega o EXE gerado pelo PyInstaller.
; NOTA: Assumindo que o PyInstaller gera "dist\Rodam.exe" (onefile)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Se tiver outros arquivos (imagens, configs padrão), adicione aqui
; Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
