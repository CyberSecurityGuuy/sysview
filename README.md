# sysview

Live system monitor in your terminal — CPU, memory, disk, network and top processes at a glance. Refreshes every 2 seconds.

```
                      sysview  ·  2026-04-24  13:37:59
╭─────────────── CPU  4 MHz  34.4% ───────────────╮  ╭── Memory  79.9% ──╮
│  CPU0  ███████████░░░░░░░░░  57.1%              │  │  RAM  ███████░░░░ │
│  CPU1  ██████░░░░░░░░░░░░░░  33.3%              │  │  SWP  ██████░░░░░ │
│  ...                                             │  ╰───────────────────╯
╰─────────────────────────────────────────────────╯
```

## What it shows

| Panel | Details |
|---|---|
| **CPU** | Per-core usage + frequency |
| **Memory** | RAM & Swap with bar charts |
| **Disk** | All mounted volumes |
| **Network** | Bytes/packets sent & received |
| **Top Processes** | Top 10 by CPU usage |

## Requirements

- Python 3.9+
- `rich >= 13.0`
- `psutil >= 5.9`

## How to use

**1. Clone the repo**
```bash
git clone https://github.com/CyberSecurityGuuy/sysview.git
cd sysview
```

**2. Install dependencies**
```bash
pip3 install rich psutil
```

**3. Run**
```bash
python3 sysview/main.py
```

The dashboard launches immediately and refreshes every **2 seconds**.  
Press **`Ctrl + C`** to quit.

---

### Optional — install as a command

```bash
pip3 install -e .
sysview
```

After this you can just type `sysview` anywhere in your terminal.
