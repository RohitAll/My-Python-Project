"""
System Information & Diagnostics Tools
Provides CPU, RAM, Disk, Battery, Network, Time, and Hardware information.
"""

import psutil
import platform
import socket
import datetime
from typing import Dict, Any

from tools.registry import BaseTool, tool_registry


class GetCpuUsageTool(BaseTool):
    name = "get_cpu_usage"
    description = "Get current overall CPU usage percentage and core counts."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        percent = psutil.cpu_percent(interval=0.5)
        count_logical = psutil.cpu_count(logical=True)
        count_physical = psutil.cpu_count(logical=False)
        return {
            "usage_percent": percent,
            "logical_cores": count_logical,
            "physical_cores": count_physical,
        }


class GetRamUsageTool(BaseTool):
    name = "get_ram_usage"
    description = "Get current system RAM memory usage statistics."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent,
        }


class GetDiskUsageTool(BaseTool):
    name = "get_disk_usage"
    description = "Get disk storage usage statistics for the primary drive."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        disk = psutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        }


class GetBatteryStatusTool(BaseTool):
    name = "get_battery_status"
    description = "Get laptop battery percentage and charging status."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        battery = psutil.sensors_battery()
        if battery is None:
            return {"has_battery": False, "message": "No battery detected (Desktop system or VM)."}

        return {
            "has_battery": True,
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secs_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited",
        }


class GetSystemInfoTool(BaseTool):
    name = "get_system_info"
    description = "Get summary of operating system, architecture, and hostname."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "processor": platform.processor(),
        }


class GetCurrentTimeTool(BaseTool):
    name = "get_current_time"
    description = "Get current date, time, timezone, and day of week."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        now = datetime.datetime.now()
        return {
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%A, %B %d, %Y"),
            "time": now.strftime("%I:%M:%S %p"),
            "day_of_week": now.strftime("%A"),
        }


class GetNetworkInfoTool(BaseTool):
    name = "get_network_info"
    description = "Get active IP addresses and network connection status."
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "127.0.0.1"

        return {
            "hostname": hostname,
            "local_ip": local_ip,
        }


def register_system_tools():
    tool_registry.register(GetCpuUsageTool())
    tool_registry.register(GetRamUsageTool())
    tool_registry.register(GetDiskUsageTool())
    tool_registry.register(GetBatteryStatusTool())
    tool_registry.register(GetSystemInfoTool())
    tool_registry.register(GetCurrentTimeTool())
    tool_registry.register(GetNetworkInfoTool())


register_system_tools()
