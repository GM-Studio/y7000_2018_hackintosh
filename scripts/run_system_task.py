import paramiko, time, sys
BASE = r"E:\ai_workflow\demo_java\docs\macos-install"
PW = open(BASE + r"\runs\a-238-20261107\private\a-login-password", encoding="utf-8").read().strip()
local_ps, task, done_name, log_name, timeout_s = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.0.238", 22, "sc", PW, timeout=20, allow_agent=False, look_for_keys=False)
s = c.open_sftp()
remote_ps = r"C:\Users\sc\AppData\Local\Temp\%s.ps1" % task
s.put(local_ps, remote_ps)
s.close()
def run(cmd, t=180):
    si,so,se=c.exec_command(cmd, timeout=t)
    return so.read().decode("gbk","replace").strip(), se.read().decode("gbk","replace").strip()
run(r'schtasks /Delete /TN "%s" /F' % task)
try: s.open_sftp().remove(r"C:\Users\sc\AppData\Local\Temp\%s" % done_name)
except Exception: pass
o,e = run(r'schtasks /Create /TN "%s" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File %s" /SC ONCE /ST 00:00 /RL HIGHEST /RU SYSTEM /F' % (task, remote_ps))
print("CREATE:", (o or e)[:160])
fix = 'powershell -NoProfile -Command "$x=Get-ScheduledTask -TaskName \'%s\'; $x.Settings.DisallowStartIfOnBatteries=$false; $x.Settings.StopIfGoingOnBatteries=$false; $x.Settings.ExecutionTimeLimit=\'PT0S\'; Set-ScheduledTask -TaskName \'%s\' -Settings $x.Settings | Out-Null; \'SETTINGS_OK\'"' % (task, task)
o,e = run(fix)
print("SETTINGS:", (o or e)[:160])
run(r'schtasks /Run /TN "%s"' % task)
s = c.open_sftp()
deadline = time.time() + timeout_s
ok = False
while time.time() < deadline:
    try:
        s.stat(r"C:\Users\sc\AppData\Local\Temp\%s" % done_name); ok = True; break
    except IOError:
        time.sleep(3)
log = "(no log)"
if ok:
    try:
        with s.open(r"C:\Users\sc\AppData\Local\Temp\%s" % log_name, "rb") as fh: log = fh.read().decode("utf-8-sig","replace")
    except IOError: pass
s.close()
run(r'schtasks /Delete /TN "%s" /F' % task)
c.close()
print("DONE" if ok else "TIMEOUT")
print(log[:1200])
