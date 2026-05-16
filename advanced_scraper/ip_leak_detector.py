"""
IP Leak Detector - Critical safety system for preventing IP exposure.
Monitors IP status, detects leaks, and automatically halts operations if needed.
"""

import time
import threading
import requests
from datetime import datetime
from typing import Callable, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class IPStatus:
    """Current IP status snapshot."""
    current_ip: str
    country: str
    city: str = ""
    isp: str = ""
    is_vpn: bool = False
    is_proxy: bool = False
    is_datacenter: bool = False
    risk_level: RiskLevel = RiskLevel.LOW
    timestamp: datetime = field(default_factory=datetime.now)
    
    def should_halt(self) -> bool:
        """Determine if process should halt."""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


class IPLeakDetector:
    """
    Advanced IP leak detection system.
    Monitors IP across multiple endpoints and halts on leak detection.
    """
    
    # Multiple IP detection endpoints (redundancy)
    IP_ENDPOINTS = [
        "https://api.ipify.org?format=json",
        "https://ipapi.co/json/",
        "https://ipinfo.io/json",
        "https://api.myip.com",
        "https://geoip-api.com/api/geoip/check",
    ]
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.current_status: Optional[IPStatus] = None
        self.ip_history: list = []
        self.monitoring = False
        self.lock = threading.Lock()
        self.leak_callbacks: list[Callable[[IPStatus], None]] = []
        self.halt_callbacks: list[Callable[[str], None]] = []
    
    def register_leak_callback(self, callback: Callable[[IPStatus], None]):
        """Register callback for leak detection."""
        self.leak_callbacks.append(callback)
    
    def register_halt_callback(self, callback: Callable[[str], None]):
        """Register callback for halt events."""
        self.halt_callbacks.append(callback)
    
    def check_ip_status(self) -> IPStatus:
        """
        Check current IP status across multiple endpoints.
        Returns most consistent result from all endpoints.
        """
        results = []
        
        for endpoint in self.IP_ENDPOINTS:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse different endpoint formats
                    if "ip" in data:
                        ip = data.get("ip")
                    elif "query" in data:
                        ip = data.get("query")
                    else:
                        continue
                    
                    status = IPStatus(
                        current_ip=ip,
                        country=data.get("country", "Unknown"),
                        city=data.get("city", ""),
                        isp=data.get("org", data.get("isp", "")),
                        is_vpn=data.get("is_vpn", False),
                        is_proxy=data.get("is_proxy", False),
                        is_datacenter=data.get("is_datacenter", False),
                    )
                    
                    # Assess risk
                    status.risk_level = self._assess_risk(status)
                    results.append(status)
            
            except (requests.RequestException, ValueError):
                continue
        
        if not results:
            raise Exception("Failed to check IP status - all endpoints unreachable")
        
        # Use first successful result (endpoints should be consistent)
        with self.lock:
            self.current_status = results[0]
            self.ip_history.append(results[0])
        
        return results[0]
    
    def _assess_risk(self, status: IPStatus) -> RiskLevel:
        """Assess risk level based on IP characteristics."""
        risk_score = 0
        
        if status.is_vpn:
            risk_score += 10
        if status.is_proxy:
            risk_score += 15
        if status.is_datacenter:
            risk_score += 5
        
        # Suspicious countries (example list - customize as needed)
        suspicious_countries = ["KP", "IR", "SY"]  # DPRK, Iran, Syria
        if status.country in suspicious_countries:
            risk_score += 20
        
        if risk_score >= 25:
            return RiskLevel.CRITICAL
        elif risk_score >= 15:
            return RiskLevel.HIGH
        elif risk_score >= 5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def should_proceed(self) -> Tuple[bool, str]:
        """
        Determine if it's safe to proceed with scraping.
        Returns (should_proceed, reason).
        """
        if not self.current_status:
            return False, "IP status not checked"
        
        status = self.current_status
        
        if status.risk_level == RiskLevel.CRITICAL:
            return False, f"⛔ CRITICAL RISK: Detected datacenter/proxy/VPN in {status.country}"
        
        if status.risk_level == RiskLevel.HIGH:
            return False, f"🔴 HIGH RISK: IP characteristics indicate potential leak"
        
        return True, "✅ Safe to proceed"
    
    def display_status(self) -> Panel:
        """Display current IP status in rich panel."""
        if not self.current_status:
            return Panel(
                "[red]❌ IP status not checked[/red]",
                title="[bold]IP STATUS[/bold]",
            )
        
        status = self.current_status
        
        # Color based on risk
        color_map = {
            RiskLevel.LOW: "green",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.HIGH: "orange",
            RiskLevel.CRITICAL: "red",
        }
        color = color_map[status.risk_level]
        
        table = Table(show_header=False, box=None)
        
        table.add_row("[bold]IP Address[/bold]", f"[{color}]{status.current_ip}[/{color}]")
        table.add_row("[bold]Country[/bold]", status.country)
        if status.city:
            table.add_row("[bold]City[/bold]", status.city)
        if status.isp:
            table.add_row("[bold]ISP[/bold]", status.isp)
        
        table.add_row(
            "[bold]VPN Active[/bold]",
            "[red]YES[/red]" if status.is_vpn else "[green]NO[/green]"
        )
        table.add_row(
            "[bold]Proxy Active[/bold]",
            "[red]YES[/red]" if status.is_proxy else "[green]NO[/green]"
        )
        table.add_row(
            "[bold]Datacenter[/bold]",
            "[red]YES[/red]" if status.is_datacenter else "[green]NO[/green]"
        )
        
        risk_indicator = {
            RiskLevel.LOW: "✅ LOW",
            RiskLevel.MEDIUM: "⚠️  MEDIUM",
            RiskLevel.HIGH: "🔴 HIGH",
            RiskLevel.CRITICAL: "⛔ CRITICAL",
        }
        
        table.add_row(
            "[bold]Risk Level[/bold]",
            f"[{color}]{risk_indicator[status.risk_level]}[/{color}]"
        )
        
        return Panel(
            table,
            title=f"[bold {color}]🌐 IP STATUS[/bold {color}]",
            border_style=color,
            padding=(1, 2),
        )
    
    def start_monitoring(self, interval: int = 60, check_on_interval: bool = True):
        """
        Start background monitoring of IP status.
        
        Args:
            interval: Check interval in seconds
            check_on_interval: If True, check immediately on start
        """
        if self.monitoring:
            self.console.print("[yellow]⚠️  Monitoring already running[/yellow]")
            return
        
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    previous_ip = self.current_status.current_ip if self.current_status else None
                    new_status = self.check_ip_status()
                    
                    # Check for IP change (leak indicator)
                    if previous_ip and new_status.current_ip != previous_ip:
                        self._trigger_leak_alert(new_status)
                    
                    # Check for risk level increase
                    if (self.current_status and 
                        new_status.risk_level.value > self.current_status.risk_level.value):
                        self._trigger_leak_alert(new_status)
                    
                    time.sleep(interval)
                
                except Exception as e:
                    self.console.print(f"[red]❌ Monitoring error: {e}[/red]")
                    time.sleep(interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        
        if check_on_interval:
            try:
                self.check_ip_status()
            except Exception as e:
                self.console.print(f"[red]❌ Initial IP check failed: {e}[/red]")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        self.console.print("[yellow]📊 Monitoring stopped[/yellow]")
    
    def _trigger_leak_alert(self, status: IPStatus):
        """Trigger leak detection callbacks."""
        self.console.print(
            Panel(
                f"[red bold]🚨 LEAK DETECTED[/red bold]\n\n"
                f"IP: {status.current_ip}\n"
                f"Country: {status.country}\n"
                f"Risk: {status.risk_level.value}",
                border_style="red",
                title="[red bold]SECURITY ALERT[/red bold]",
            )
        )
        
        for callback in self.leak_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.console.print(f"[red]❌ Callback error: {e}[/red]")
    
    def _trigger_halt(self, reason: str):
        """Trigger halt callbacks."""
        for callback in self.halt_callbacks:
            try:
                callback(reason)
            except Exception as e:
                self.console.print(f"[red]❌ Halt callback error: {e}[/red]")
    
    def notify_and_halt(self) -> Tuple[bool, str]:
        """
        Check status and halt if unsafe.
        Returns (should_continue, message).
        """
        try:
            self.check_ip_status()
        except Exception as e:
            return False, f"❌ IP check failed: {e}"
        
        should_proceed, reason = self.should_proceed()
        
        if not should_proceed:
            self.console.print(self.display_status())
            self.console.print(
                Panel(
                    f"[red bold]{reason}[/red bold]\n\n"
                    "Process halted for your safety.",
                    border_style="red",
                    title="[red bold]⛔ HALT[/red bold]",
                )
            )
            self._trigger_halt(reason)
        
        return should_proceed, reason
    
    def get_ip_history(self, limit: Optional[int] = None) -> list:
        """Get historical IP status records."""
        with self.lock:
            if limit:
                return self.ip_history[-limit:]
            return self.ip_history.copy()
    
    def export_report(self, filename: str = "ip_report.txt"):
        """Export IP monitoring report to file."""
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("IP LEAK DETECTION REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            
            if self.current_status:
                f.write("CURRENT STATUS:\n")
                f.write(f"  IP: {self.current_status.current_ip}\n")
                f.write(f"  Country: {self.current_status.country}\n")
                f.write(f"  Risk Level: {self.current_status.risk_level.value}\n")
                f.write(f"  VPN: {self.current_status.is_vpn}\n")
                f.write(f"  Proxy: {self.current_status.is_proxy}\n")
                f.write("\n")
            
            if self.ip_history:
                f.write("HISTORY:\n")
                for status in self.ip_history[-20:]:  # Last 20
                    f.write(
                        f"  {status.timestamp}: {status.current_ip} "
                        f"({status.country}) - {status.risk_level.value}\n"
                    )
        
        self.console.print(f"[green]✅ Report exported to {filename}[/green]")


# CLI Interface
if __name__ == "__main__":
    detector = IPLeakDetector()
    
    print("\n🌐 IP Leak Detector - Checking your IP status...\n")
    
    try:
        status = detector.check_ip_status()
        console = Console()
        console.print(detector.display_status())
        
        should_proceed, reason = detector.should_proceed()
        print(f"\n{reason}")
        
        # Start background monitoring
        print("\n📊 Starting background monitoring (60 second interval)...")
        detector.start_monitoring(interval=60)
        
        # Run for 5 minutes
        import time
        time.sleep(300)
        
    except Exception as e:
        print(f"❌ Error: {e}")
