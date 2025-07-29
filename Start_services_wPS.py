import subprocess
import time

def query_service(server, service):
    try:
        ps_command = f"Invoke-Command -ComputerName {server} -ScriptBlock {{ (Get-Service -Name '{service}').Status }}"
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True, text=True, check=True
        )
        status = result.stdout.strip()
        return status
    except subprocess.CalledProcessError as e:
        print(f"Failed to query {service} on {server}: {e}")
        return "ERROR"

def wait_until_running(server, service, timeout=60, interval=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = query_service(server, service)
        print(f"Waiting for {service} on {server}... current status: {status}")
        if status.lower() == "running":
            return True
        time.sleep(interval)
    return False

def start_service_if_needed(server, service):
    status = query_service(server, service)
    if status.lower() != "running":
        print(f"{service} on {server} is not running (status: {status}). Attempting to start...")
        start_command = f"Invoke-Command -ComputerName {server} -ScriptBlock {{ Start-Service -Name '{service}' }}"
        subprocess.run(["powershell", "-Command", start_command])
        if wait_until_running(server, service, timeout=90):
            print(f"{service} on {server} is now running.")
        else:
            print(f"X {service} on {server} failed to start within the timeout.")
    else:
        print(f"{service} on {server} is already running.")

# 🧩 Replace with your actual servers/services
services_in_order = [
    {"server": "ADFS-SERVER",    "service": "adfssrv"},
    {"server": "FORTIFY-SERVER", "service": "FortifyTomcat9"},
    {"server": "SONAR-SERVER",   "service": "SonarQube"}
]

# 🔁 Enforce strict startup order
for step in services_in_order:
    start_service_if_needed(step["server"], step["service"])
