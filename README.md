# Start_ServicesPY# Windows Service Orchestrator

This Python script ensures critical Windows services are started in a specific order across multiple remote servers. It's intended for use in environments where certain service dependencies must be respected (e.g., ADFS → Fortify → SonarQube) during system boot or recovery.

##  Features

- Queries the status of services on remote Windows servers
- Starts services that are not running
- Enforces a strict start-up order
- Waits for each service to report a `RUNNING` state before continuing
- No third-party Python libraries required

## 🖥 Use Case

For example, after a reboot:
1. TestService on `Server1` must be running
2. Apache on `WebDev server` starts next
3. SonarQube on `SONAR-SERVER` starts last

