import subprocess, glob
r = subprocess.run(["powershell","-Command",
    "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | Select-Object -ExpandProperty CommandLine"],
    capture_output=True, text=True)
alive = any("run_ladder" in l for l in r.stdout.splitlines())
n = len(glob.glob(r"C:\Users\chuyo\repro-pretrain\runs\ladder_honmaru_*.json"))
print(f"ALIVE {alive} COUNT {n}")
