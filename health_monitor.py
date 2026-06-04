"""
System Health Monitor
=====================
Author: [Your Name]
Description: Monitors CPU, memory, disk, and network usage.
             Logs results to a text report and alerts on high usage.
"""

import psutil
import datetime
import os
import platform
import socket


# ─── CONFIG ────────────────────────────────────────────────────────────────────
CPU_THRESHOLD    = 85   # % — alert if CPU usage exceeds this
MEMORY_THRESHOLD = 80   # % — alert if RAM usage exceeds this
DISK_THRESHOLD   = 90   # % — alert if disk usage exceeds this
REPORT_FILE      = "health_report.txt"
# ───────────────────────────────────────────────────────────────────────────────


def get_system_info():
    """Return basic info about the machine."""
    return {
        "hostname": socket.gethostname(),
        "os":       platform.system() + " " + platform.version(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_cpu_usage():
    """Return CPU usage percentage (sampled over 1 second)."""
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    """Return memory stats as a dict."""
    mem = psutil.virtual_memory()
    return {
        "total_gb":  round(mem.total / (1024 ** 3), 2),
        "used_gb":   round(mem.used  / (1024 ** 3), 2),
        "free_gb":   round(mem.free  / (1024 ** 3), 2),
        "percent":   mem.percent,
    }


def get_disk_usage(path="C:\\"):
    """Return disk usage stats for the given path."""
    disk = psutil.disk_usage(path)
    return {
        "path":      path,
        "total_gb":  round(disk.total / (1024 ** 3), 2),
        "used_gb":   round(disk.used  / (1024 ** 3), 2),
        "free_gb":   round(disk.free  / (1024 ** 3), 2),
        "percent":   disk.percent,
    }


def get_top_processes(n=5):
    """Return the top N processes by CPU usage."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    # Sort by CPU usage descending
    return sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)[:n]


def get_network_stats():
    """Return bytes sent and received since boot."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb":     round(net.bytes_sent     / (1024 ** 2), 2),
        "bytes_received_mb": round(net.bytes_recv / (1024 ** 2), 2),
    }


def check_alerts(cpu, memory, disk):
    """Return a list of alert messages for values above thresholds."""
    alerts = []
    if cpu >= CPU_THRESHOLD:
        alerts.append(f"⚠️  HIGH CPU USAGE: {cpu}% (threshold: {CPU_THRESHOLD}%)")
    if memory["percent"] >= MEMORY_THRESHOLD:
        alerts.append(f"⚠️  HIGH MEMORY USAGE: {memory['percent']}% (threshold: {MEMORY_THRESHOLD}%)")
    if disk["percent"] >= DISK_THRESHOLD:
        alerts.append(f"⚠️  HIGH DISK USAGE: {disk['percent']}% (threshold: {DISK_THRESHOLD}%)")
    return alerts


def build_report(info, cpu, memory, disk, network, top_procs, alerts):
    """Assemble all stats into a formatted report string."""
    sep = "=" * 60

    lines = [
        sep,
        "         SYSTEM HEALTH REPORT",
        sep,
        f"  Host      : {info['hostname']}",
        f"  OS        : {info['os']}",
        f"  CPU Cores : {info['cpu_cores']}",
        f"  Timestamp : {info['timestamp']}",
        "",
        "── CPU ──────────────────────────────────────────────────",
        f"  Usage     : {cpu}%",
        "",
        "── MEMORY ───────────────────────────────────────────────",
        f"  Total     : {memory['total_gb']} GB",
        f"  Used      : {memory['used_gb']} GB  ({memory['percent']}%)",
        f"  Free      : {memory['free_gb']} GB",
        "",
        "── DISK ─────────────────────────────────────────────────",
        f"  Path      : {disk['path']}",
        f"  Total     : {disk['total_gb']} GB",
        f"  Used      : {disk['used_gb']} GB  ({disk['percent']}%)",
        f"  Free      : {disk['free_gb']} GB",
        "",
        "── NETWORK (since boot) ─────────────────────────────────",
        f"  Sent      : {network['bytes_sent_mb']} MB",
        f"  Received  : {network['bytes_received_mb']} MB",
        "",
        "── TOP 5 PROCESSES BY CPU ───────────────────────────────",
    ]

    for proc in top_procs:
        lines.append(
            f"  [{proc['pid']:>6}]  {proc['name']:<30} "
            f"CPU: {proc['cpu_percent']:>5}%   MEM: {proc['memory_percent']:>5.1f}%"
        )

    lines.append("")
    if alerts:
        lines.append("── ALERTS ───────────────────────────────────────────────")
        for alert in alerts:
            lines.append(f"  {alert}")
    else:
        lines.append("── ALERTS ───────────────────────────────────────────────")
        lines.append("  ✅  All systems within normal thresholds.")

    lines.append(sep)
    return "\n".join(lines)


def save_report(report_text):
    """Append the report to the log file."""
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(report_text + "\n\n")
    print(f"[+] Report saved to '{REPORT_FILE}'")


def main():
    print("[*] Running System Health Monitor...")

    info       = get_system_info()
    cpu        = get_cpu_usage()
    memory     = get_memory_usage()
    disk       = get_disk_usage()
    network    = get_network_stats()
    top_procs  = get_top_processes()
    alerts     = check_alerts(cpu, memory, disk)

    report = build_report(info, cpu, memory, disk, network, top_procs, alerts)

    # Print to terminal
    print(report)

    # Save to file
    save_report(report)


if __name__ == "__main__":
    main()
