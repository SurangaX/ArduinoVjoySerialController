Set WshShell = CreateObject("WScript.Shell")
ScriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
WshShell.Run "pythonw """ & ScriptDir & "com_to_vjoy_gui.py""", 0, False
