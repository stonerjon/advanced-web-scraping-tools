"""
Metrics HUD - Real-time monitoring dashboard for all scraping operations.
Displays API usage, IP rotation, success rates, and resource utilization.
"""

import time
import threading
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn
from rich.text import Text

import psutil


class MetricType(Enum):
    """Types of metrics."""
    REQUESTS = "requests"
    SUCCESS = "success"
    ERROR = "error"
    API_CALLS = "api_calls"
    DATA_BYTES = "data_bytes"
    IP_CHANGES = "ip_changes"
    PROXY_FAILURES = "proxy_failures"


@dataclass
class Metric:
    """Individual metric data point."""
    type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self, window_size: int = 300):  # 5 minute window
        self.window_size = window_size
        self.metrics: Dict[MetricType, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.sources_used: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()
    
    def record(self, metric: Metric):
        """Record a metric."""
        with self.lock:
            self.metrics[metric.type].append(metric)
    
    def record_request(self, success: bool, bytes_: int = 0, source: Optional[str] = None):
        """Record a request."""
        self.record(Metric(MetricType.REQUESTS, 1))
        self.record(Metric(MetricType.SUCCESS if success else MetricType.ERROR, 1))
        if bytes_:
            self.record(Metric(MetricType.DATA_BYTES, bytes_))
        if source:
            with self.lock:
                self.sources_used[source] += 1
    
    def get_rate(self, metric_type: MetricType, interval: int = 60) -> float:
        """Get metric rate per second."""
        with self.lock:
            metrics = list(self.metrics[metric_type])
        
        if not metrics:
            return 0.0
        
        now = datetime.now()
        recent = [
            m for m in metrics
            if (now - m.timestamp).total_seconds() <= interval
        ]
        
        return len(recent) / interval if interval > 0 else 0.0
    
    def get_total(self, metric_type: MetricType) -> float:
        """Get total for metric type."""
        with self.lock:
            return sum(m.value for m in self.metrics[metric_type])
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        total_requests = self.get_total(MetricType.REQUESTS)
        successful = self.get_total(MetricType.SUCCESS)
        
        if total_requests == 0:
            return 0.0
        
        return (successful / total_requests) * 100
    
    def get_top_sources(self, n: int = 5) -> List[tuple]:
        """Get top N data sources."""
        with self.lock:
            sorted_sources = sorted(
                self.sources_used.items(),
                key=lambda x: x[1],
                reverse=True
            )
        
        return sorted_sources[:n]


class MetricsHUD:
    """Real-time metrics dashboard HUD."""
    
    def __init__(self, collector: Optional[MetricsCollector] = None):
        self.collector = collector or MetricsCollector()
        self.console = Console()
        self.running = False
        self.start_time = datetime.now()
    
    def render_overview(self) -> Panel:
        """Render overview metrics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        uptime_str = self._format_duration(uptime)
        
        overview_table = Table(show_header=False, box=None)
        
        overview_table.add_row(
            "Total Requests",
            f"[cyan]{int(self.collector.get_total(MetricType.REQUESTS))}[/cyan]"
        )
        overview_table.add_row(
            "Success Rate",
            f"[green]{self.collector.get_success_rate():.1f}%[/green]"
        )
        overview_table.add_row(
            "Data Transferred",
            f"[yellow]{self._format_bytes(self.collector.get_total(MetricType.DATA_BYTES))}[/yellow]"
        )
        overview_table.add_row(
            "Uptime",
            f"[magenta]{uptime_str}[/magenta]"
        )
        
        return Panel(
            overview_table,
            title="[bold cyan]📊 OVERVIEW[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    
    def render_rates(self) -> Panel:
        """Render rate metrics."""
        rates_table = Table(show_header=True, box=None)
        rates_table.add_column("Metric", style="cyan")
        rates_table.add_column("Rate", style="green")
        
        rates_table.add_row(
            "Requests/sec",
            f"{self.collector.get_rate(MetricType.REQUESTS):.2f}"
        )
        rates_table.add_row(
            "Success/sec",
            f"{self.collector.get_rate(MetricType.SUCCESS):.2f}"
        )
        rates_table.add_row(
            "Errors/sec",
            f"{self.collector.get_rate(MetricType.ERROR):.2f}"
        )
        rates_table.add_row(
            "Data/sec",
            f"{self._format_bytes(self.collector.get_rate(MetricType.DATA_BYTES))} /s"
        )
        
        return Panel(
            rates_table,
            title="[bold yellow]⚡ RATES[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    
    def render_sources(self) -> Panel:
        """Render top data sources."""
        sources_table = Table(title="[bold green]📦 TOP SOURCES[/bold green]", show_header=True)
        sources_table.add_column("Source", style="cyan")
        sources_table.add_column("Calls", style="green")
        
        for source, count in self.collector.get_top_sources():
            sources_table.add_row(source, str(count))
        
        return Panel(
            sources_table,
            border_style="green",
            padding=(1, 2),
        )
    
    def render_system_resources(self) -> Panel:
        """Render system resource usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources_table = Table(show_header=False, box=None)
        
        # CPU
        cpu_bar = "█" * int(cpu_percent / 5) + "░" * (20 - int(cpu_percent / 5))
        resources_table.add_row(
            "CPU",
            f"[yellow]{cpu_bar}[/yellow] {cpu_percent:.1f}%"
        )
        
        # Memory
        mem_percent = memory.percent
        mem_bar = "█" * int(mem_percent / 5) + "░" * (20 - int(mem_percent / 5))
        resources_table.add_row(
            "Memory",
            f"[cyan]{mem_bar}[/cyan] {mem_percent:.1f}%"
        )
        
        # Disk
        disk_percent = disk.percent
        disk_bar = "█" * int(disk_percent / 5) + "░" * (20 - int(disk_percent / 5))
        resources_table.add_row(
            "Disk",
            f"[magenta]{disk_bar}[/magenta] {disk_percent:.1f}%"
        )
        
        return Panel(
            resources_table,
            title="[bold magenta]💻 RESOURCES[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
    
    def render_full_dashboard(self) -> Layout:
        """Render full dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        
        layout["header"].update(Panel(
            "[bold cyan]🎯 ADVANCED SCRAPER METRICS HUD[/bold cyan]",
            border_style="cyan",
        ))
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        
        layout["left"].split_column(
            Layout(self.render_overview()),
            Layout(self.render_rates()),
        )
        
        layout["right"].split_column(
            Layout(self.render_sources()),
            Layout(self.render_system_resources()),
        )
        
        layout["footer"].update(Panel(
            f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="dim",
        ))
        
        return layout
    
    def start_live_display(self, interval: float = 2.0):
        """Start live updating display."""
        self.running = True
        
        try:
            with Live(
                self.render_full_dashboard(),
                refresh_per_second=1 / interval,
                console=self.console,
            ) as live:
                while self.running:
                    live.update(self.render_full_dashboard())
                    time.sleep(interval)
        except KeyboardInterrupt:
            self.running = False
    
    @staticmethod
    def _format_bytes(bytes_: float) -> str:
        """Format bytes to human readable."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_ < 1024:
                return f"{bytes_:.1f} {unit}"
            bytes_ /= 1024
        return f"{bytes_:.1f} TB"
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration to human readable."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# Example usage
if __name__ == "__main__":
    collector = MetricsCollector()
    hud = MetricsHUD(collector)
    
    # Simulate some metrics
    import random
    
    def simulate_metrics():
        while hud.running:
            for i in range(random.randint(1, 5)):
                success = random.random() > 0.15  # 85% success rate
                bytes_ = random.randint(1000, 100000) if success else 0
                source = random.choice(["hunter_io", "clearbit", "github_api", "twitter"])
                
                collector.record_request(success, bytes_, source)
            
            time.sleep(1)
    
    # Start metrics thread
    metrics_thread = threading.Thread(target=simulate_metrics, daemon=True)
    metrics_thread.start()
    
    # Start HUD
    hud.start_live_display(interval=1.0)
