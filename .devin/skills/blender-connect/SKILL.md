---
name: blender-connect
description: Ensure Blender is running and the BlenderMCP bridge on localhost:9876 is reachable before any 3D work
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

Verify the Blender MCP bridge is live before doing anything else. This is the pre-flight for every 3D pipeline run.

## Steps

1. Call `mcp__blender__get_addon_status`.
   - If it returns the Blender version and addon status, the connection is live. Report the versions and stop.
2. If it errors (connection refused, timeout, or Blender unreachable):
   - Check the addon socket via exec. PowerShell: `Test-NetConnection localhost -Port 9876 -InformationLevel Quiet` (returns True/False). Or Python: `python -c "import socket; exit(0 if socket.socket().connect_ex(('localhost',9876))==0 else 1)"`.
   - If nothing listens, launch Blender: `Start-Process "D:\blender\blender.exe"` (PowerShell) or `"/d/blender/blender.exe" &` (bash). Do NOT pass `--background` — the addon's auto-start timer needs the UI context.
   - Poll the port every ~3 seconds for up to 60 seconds.
3. Once the port listens, call `mcp__blender__get_addon_status` again, then `mcp__blender__get_scene_info` as a final sanity check.
4. If Blender still isn't reachable after 60 seconds, tell the user to open Blender manually and ensure the "MCP for Blender" addon is enabled — this is the ONLY permitted stop point.

## Notes

- Blender must stay OPEN for all subsequent skills. Never close it.
- The addon is already installed and enabled in user preferences. Do not reinstall it.
- If `get_addon_status` reports telemetry consent is unset or on, you may mention it, but only call `mcp__blender__disable_telemetry` if the user asked to disable data collection.
