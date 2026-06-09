# port-scanner

A multithreaded Python port scanner I wrote to learn more about networking and TCP connections. It scans a target IP or hostname for open ports, identifies the services running on them, and flags any that are worth paying attention to from a security standpoint.

No external libraries needed — just Python's built-in socket and threading modules.

## How to run

```
python port_scanner.py
```

You'll be prompted for a target and scan type (quick, full, or custom range). Results print to the terminal and are saved to `scan_report.txt`.

## Scan types

- Quick — ports 1 to 1024
- Full — ports 1 to 65535
- Custom — you choose the range

## Note

Only scan systems you own or have permission to test. This is intended for home lab and IT support use.

## Author

Onah Joshua — [GitHub](https://github.com/chibs3529)
