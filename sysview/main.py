#!/usr/bin/env python3
import time
import psutil
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import BarColumn, Progress, TextColumn
from rich.console import Console, Group
from rich.text import Text
from rich import box

console = Console()


def _bar(value: float, width: int = 20) -> str:
    filled = int(value / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _color(value: float) -> str:
    if value < 60:
        return "green"
    if value < 85:
        return "yellow"
    return "red"


def build_layout() -> Group:
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    # ── CPU ──────────────────────────────────────────────────────────────
    cpu_total = psutil.cpu_percent(interval=None)
    cpu_per = psutil.cpu_percent(percpu=True)
    freq = psutil.cpu_freq()

    cpu_table = Table(box=None, show_header=False, padding=(0, 1))
    cpu_table.add_column(width=6, justify="right")
    cpu_table.add_column(width=22)
    cpu_table.add_column(width=6, justify="right")

    for i, pct in enumerate(cpu_per):
        c = _color(pct)
        cpu_table.add_row(
            f"[dim]CPU{i}[/]",
            f"[{c}]{_bar(pct)}[/]",
            f"[{c}]{pct:5.1f}%[/]",
        )

    freq_str = f"{freq.current:.0f} MHz" if freq else "—"
    cpu_panel = Panel(
        cpu_table,
        title=f"[bold cyan]CPU[/]  [dim]{freq_str}[/]  [bold {_color(cpu_total)}]{cpu_total:.1f}%[/]",
        border_style="cyan",
        padding=(0, 1),
    )

    # ── Memory ───────────────────────────────────────────────────────────
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    mem_color = _color(mem.percent)
    swap_color = _color(swap.percent)

    mem_table = Table(box=None, show_header=False, padding=(0, 1))
    mem_table.add_column(width=5, justify="right")
    mem_table.add_column(width=22)
    mem_table.add_column(width=14, justify="right")

    mem_table.add_row(
        "[dim]RAM[/]",
        f"[{mem_color}]{_bar(mem.percent)}[/]",
        f"[{mem_color}]{mem.used/1e9:.1f}/{mem.total/1e9:.1f} GB[/]",
    )
    mem_table.add_row(
        "[dim]SWP[/]",
        f"[{swap_color}]{_bar(swap.percent)}[/]",
        f"[{swap_color}]{swap.used/1e9:.1f}/{swap.total/1e9:.1f} GB[/]",
    )

    mem_panel = Panel(
        mem_table,
        title=f"[bold magenta]Memory[/]  [bold {mem_color}]{mem.percent:.1f}%[/]",
        border_style="magenta",
        padding=(0, 1),
    )

    # ── Disk ─────────────────────────────────────────────────────────────
    disk_table = Table(box=None, show_header=False, padding=(0, 1))
    disk_table.add_column(width=12, overflow="fold")
    disk_table.add_column(width=20)
    disk_table.add_column(width=16, justify="right")

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        c = _color(usage.percent)
        disk_table.add_row(
            f"[dim]{part.mountpoint}[/]",
            f"[{c}]{_bar(usage.percent)}[/]",
            f"[{c}]{usage.used/1e9:.1f}/{usage.total/1e9:.1f} GB[/]",
        )

    disk_panel = Panel(
        disk_table,
        title="[bold yellow]Disk[/]",
        border_style="yellow",
        padding=(0, 1),
    )

    # ── Network ──────────────────────────────────────────────────────────
    net = psutil.net_io_counters()
    net_table = Table(box=None, show_header=False, padding=(0, 1))
    net_table.add_column(width=8)
    net_table.add_column(width=18, justify="right")

    net_table.add_row("[dim]↑ Sent[/]",   f"[green]{net.bytes_sent/1e6:>10.1f} MB[/]")
    net_table.add_row("[dim]↓ Recv[/]",   f"[blue]{net.bytes_recv/1e6:>10.1f} MB[/]")
    net_table.add_row("[dim]Pkts ↑[/]",   f"[dim]{net.packets_sent:>10,}[/]")
    net_table.add_row("[dim]Pkts ↓[/]",   f"[dim]{net.packets_recv:>10,}[/]")

    net_panel = Panel(
        net_table,
        title="[bold blue]Network[/]",
        border_style="blue",
        padding=(0, 1),
    )

    # ── Top Processes ────────────────────────────────────────────────────
    procs = sorted(
        psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]),
        key=lambda p: p.info["cpu_percent"] or 0,
        reverse=True,
    )[:10]

    proc_table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim", padding=(0, 1))
    proc_table.add_column("PID",    width=7,  justify="right")
    proc_table.add_column("Name",   width=22, overflow="fold")
    proc_table.add_column("CPU%",   width=7,  justify="right")
    proc_table.add_column("MEM%",   width=7,  justify="right")
    proc_table.add_column("Status", width=10)

    for p in procs:
        cpu = p.info["cpu_percent"] or 0
        mem = p.info["memory_percent"] or 0
        c = _color(cpu)
        proc_table.add_row(
            str(p.info["pid"]),
            p.info["name"] or "—",
            f"[{c}]{cpu:5.1f}[/]",
            f"{mem:5.1f}",
            f"[dim]{p.info['status']}[/]",
        )

    proc_panel = Panel(
        proc_table,
        title="[bold white]Top Processes[/]",
        border_style="white",
        padding=(0, 0),
    )

    header = Text(f" sysview  ·  {now} ", style="bold white on grey15", justify="center")

    return Group(
        header,
        Columns([cpu_panel, mem_panel], equal=True),
        Columns([disk_panel, net_panel], equal=True),
        proc_panel,
        Text("  [dim]q[/dim] quit  ·  refreshes every 2s", justify="left"),
    )


def main():
    psutil.cpu_percent(percpu=True)  # warm-up
    time.sleep(0.1)

    with Live(build_layout(), refresh_per_second=0.5, screen=True, console=console) as live:
        try:
            while True:
                time.sleep(2)
                live.update(build_layout())
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
