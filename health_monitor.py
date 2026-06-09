import psutil
import datetime
import socket
import platform


REPORT_FILE = "health_report.txt"

CPU_ALERT    = 85
MEMORY_ALERT = 80
DISK_ALERT   = 90


def system_info():
    return {
        "host": socket.gethostname(),
        "os": platform.system() + " " + platform.version(),
        "cores": psutil.cpu_count(logical=True),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def cpu_usage():
    return psutil.cpu_percent(interval=1)


def memory_usage():
    m = psutil.virtual_memory()
    return {
        "total": round(m.total / (1024 ** 3), 2),
        "used":  round(m.used  / (1024 ** 3), 2),
        "free":  round(m.free  / (1024 ** 3), 2),
        "pct":   m.percent
    }


def disk_usage(path="C:\\"):
    d = psutil.disk_usage(path)
    return {
        "path":  path,
        "total": round(d.total / (1024 ** 3), 2),
        "used":  round(d.used  / (1024 ** 3), 2),
        "free":  round(d.free  / (1024 ** 3), 2),
        "pct":   d.percent
    }


def network_stats():
    n = psutil.net_io_counters()
    return {
        "sent": round(n.bytes_sent / (1024 ** 2), 2),
        "recv": round(n.bytes_recv / (1024 ** 2), 2)
    }


def top_processes(n=5):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(procs, key=lambda x: x["cpu_percent"], reverse=True)[:n]


def check_alerts(cpu, mem, disk):
    alerts = []
    if cpu >= CPU_ALERT:
        alerts.append(f"High CPU usage: {cpu}%")
    if mem["pct"] >= MEMORY_ALERT:
        alerts.append(f"High memory usage: {mem['pct']}%")
    if disk["pct"] >= DISK_ALERT:
        alerts.append(f"High disk usage: {disk['pct']}%")
    return alerts


def build_report(info, cpu, mem, disk, net, procs, alerts):
    lines = [
        f"System Health Report",
        f"--------------------",
        f"Host      : {info['host']}",
        f"OS        : {info['os']}",
        f"CPU Cores : {info['cores']}",
        f"Time      : {info['time']}",
        f"",
        f"CPU",
        f"  Usage : {cpu}%",
        f"",
        f"Memory",
        f"  Total : {mem['total']} GB",
        f"  Used  : {mem['used']} GB ({mem['pct']}%)",
        f"  Free  : {mem['free']} GB",
        f"",
        f"Disk ({disk['path']})",
        f"  Total : {disk['total']} GB",
        f"  Used  : {disk['used']} GB ({disk['pct']}%)",
        f"  Free  : {disk['free']} GB",
        f"",
        f"Network (since boot)",
        f"  Sent     : {net['sent']} MB",
        f"  Received : {net['recv']} MB",
        f"",
        f"Top Processes by CPU",
    ]

    for p in procs:
        lines.append(
            f"  [{p['pid']:>6}]  {p['name']:<28}  cpu: {p['cpu_percent']}%  mem: {round(p['memory_percent'], 1)}%"
        )

    lines.append("")
    if alerts:
        lines.append("Alerts")
        for a in alerts:
            lines.append(f"  - {a}")
    else:
        lines.append("No alerts. All values within normal range.")

    lines.append("")
    return "\n".join(lines)


def main():
    info   = system_info()
    cpu    = cpu_usage()
    mem    = memory_usage()
    disk   = disk_usage()
    net    = network_stats()
    procs  = top_processes()
    alerts = check_alerts(cpu, mem, disk)

    report = build_report(info, cpu, mem, disk, net, procs, alerts)
    print(report)

    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Report saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
