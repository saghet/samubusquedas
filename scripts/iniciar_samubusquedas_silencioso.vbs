' SamuBusquedas (.onion v3) — Lanzador Silencioso en Segundo Plano
' Arquitecto: saghet
' Ejecuta el Watchdog de SamuBusquedas sin mostrar ninguna ventana de consola.

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\saghe\Documents\DeepWeb"
WshShell.Run "cmd /c scripts\samubusquedas_watchdog.bat", 0, False
Set WshShell = Nothing
