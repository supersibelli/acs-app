Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

' Crear el acceso directo
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\Sistema ACS.lnk")
oShellLink.TargetPath = WshShell.CurrentDirectory & "\iniciar_sistema.bat"
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.IconLocation = "C:\Windows\System32\shell32.dll,22"  ' Icono de aplicación
oShellLink.WindowStyle = 1  ' Normal
oShellLink.Description = "Sistema de Gestión para Agentes Comunitários de Saúde"
oShellLink.Save

' Mostrar mensaje de confirmación
MsgBox "Acceso directo creado en el escritorio.", 64, "Sistema ACS" 