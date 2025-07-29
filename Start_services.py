# Import necessary standard libraries
import subprocess  # Used to run system-level commands like 'sc' to interact with Windows services
import time        # Provides sleep/delay functions and timestamp-based timeout logic

# Function to check the status of a service on a given server
def query_service(server, service):
    try:
        # Run the 'sc query' command against the remote server
        # Example: sc \\SERVERNAME query servicename
        result = subprocess.run(
            ["sc", f"\\\\{server}", "query", service],
            capture_output=True,  # Capture the output so we can inspect it
            text=True,            # Return output as text (not bytes)
            check=True            # Raise CalledProcessError if command fails
        )

        # Parse each line of the command output
        for line in result.stdout.splitlines():
            # Look for the line containing "STATE", which gives us the service's status
            if "STATE" in line:
                parts = line.strip().split()     # Split line into parts
                state_code = int(parts[2])       # Get numeric state code (e.g. 4 = RUNNING)
                state_text = parts[3]            # Get state text (e.g. RUNNING, STOPPED)
                return state_code, state_text    # Return status code and human-readable state

    except subprocess.CalledProcessError as e:
        # Handle any error from the subprocess (like server unreachable, service not found, etc.)
        print(f"Failed to query service '{service}' on {server}: {e}")
        return None, "ERROR"

# Function to wait until a service on a server reaches the 'RUNNING' state
def wait_until_running(server, service, timeout=60, interval=5):
    deadline = time.time() + timeout  # Calculate the time at which we should give up
    while time.time() < deadline:
        # Check the current status of the service
        state_code, state_text = query_service(server, service)
        print(f"Waiting for {service} on {server}... current state: {state_text}")
        if state_code == 4:  # 4 = RUNNING
            return True      # Service successfully reached RUNNING state
        time.sleep(interval)  # Wait a few seconds before checking again
    return False  # Timeout reached, service did not start in time

# Function to start a service if it is not already running
def start_service_if_needed(server, service):
    # First, check the current status of the service
    state_code, state_text = query_service(server, service)

    # If the service is NOT running, try to start it
    if state_code != 4:
        print(f"{service} on {server} is not running (status: {state_text}). Attempting to start...")

        # Start the service remotely using 'sc start'
        subprocess.run(["sc", f"\\\\{server}", "start", service])

        # Wait for the service to fully reach the RUNNING state
        if wait_until_running(server, service, timeout=90):
            print(f"{service} on {server} is now running.")
        else:
            print(f"X {service} on {server} failed to start within the timeout.")
    else:
        print(f"{service} on {server} is already running.")

# Define the list of services that must be started, in the required order
# These should match your actual server and service names in production
services_in_order = [
    {"server": "ADFS-SERVER",    "service": "adfssrv"},           # ADFS must start first
    {"server": "FORTIFY-SERVER", "service": "FortifyTomcat9"},    # Fortify second "APACHE"
    {"server": "SONAR-SERVER",   "service": "SonarQube"}          # SonarQube third
]

# Main loop to start all required services in strict order
for step in services_in_order:
    start_service_if_needed(step["server"], step["service"])
