````markdown
# 🏴‍☠️ Advanced Web Scraper & Recon Toolkit

## 🎯 Key Features

### ✅ **IP Leak Detection & Prevention** 🛑
- **CRITICAL SAFETY FEATURE**: Real-time IP monitoring across 5 endpoints
- **Automatic halt** if IP leak detected
- **User notified BEFORE** process continues
- VPN/Proxy detection with risk level assessment
- IP rotation history tracking
- Background monitoring thread with callback system

### ✅ **100+ Curated Data Sources**
- **12 Categories** organized for easy access
- **Business Intelligence**: Crunchbase, ClearBit, OpenCorporates, SEC EDGAR
- **Email Finders**: Hunter.io, Snov.io, PhoneBook, Apollo.io
- **Social Media**: GitHub, Twitter/X, Reddit, YouTube, LinkedIn
- **Threat Intel**: Shodan, Censys, VirusTotal, AbuseIPDB, Malware Bazaar
- **Domain Intel**: WHOIS, DNS, MXToolbox, GeoIP, ASN Lookup
- **Finance**: CryptoCompare, Alpha Vantage, FRED, Yahoo Finance
- **Technology**: Wappalyzer, NPM, PyPI, Docker Hub, CVE Database
- **Government**: FEC Data, Congress.gov, Census Data, Court Records
- **Media**: NewsAPI, HackerNews, arXiv, Reddit
- **Job Listings**: LinkedIn, Indeed, Wellfound
- **Real Estate**: Zillow, Redfin, Property Records

### ✅ **Intelligent Proxy Wrapper**
- Logical proxy rotation & pool management
- Leak detection integration BEFORE each request
- IP safety verification before proceeding
- Proxy failure tracking & blacklisting
- Support for HTTP, HTTPS, SOCKS4, SOCKS5
- Credentials support

### ✅ **OpenCode-Style TUI Dashboard**
- Real-time metrics display (requests, success rate, data transferred)
- IP status monitoring with risk indicators
- Data sources catalog viewer
- Interactive control panel (Start/Pause/Check IP/Halt/Exit)
- Live rolling log with color-coded levels
- System resource monitoring (CPU, Memory, Disk)

### ✅ **Comprehensive Metrics HUD**
- Real-time request analytics
- Success/error rate tracking
- Data transfer accounting
- Source usage statistics
- Top performing sources
- System resource utilization (CPU, Memory, Disk)
- Live updating dashboard with 1-second refresh

### ✅ **Optional LLM Agent** (Independent from agents.py)
- **Open-WebUI Integration** for autonomous scraping
- **3 Operation Modes**:
  - **MANUAL**: Pure CLI control
  - **AUTO**: Full LLM autonomy
  - **HYBRID**: Mixed manual + LLM assistance
- Natural language task interface
- Autonomous scraping campaign planning
- Interactive LLM conversation sessions
- Session history export

### ✅ **Docker Ecosystem** (Complete Infrastructure)
- **Ollama**: Local LLM engine
- **Open-WebUI**: Branded LLM interface (port 8000)
- **PostgreSQL**: Structured data storage
- **MongoDB**: Document/JSON storage
- **Redis**: Caching & rate limiting
- **Elasticsearch**: Full-text search & log indexing
- **Prometheus**: Metrics collection
- **Grafana**: Beautiful monitoring dashboards (port 3000)

### ✅ **Production-Ready Architecture**
- Modular 21+ tool design
- Stealth engine with TLS/HTTP2 fingerprint bypassing
- AI extraction unified interface (Ollama, Groq, Anthropic, etc.)
- Automated authentication & account management
- Deep reconnaissance capabilities
- Enrichment with threat intelligence APIs
- Thread-safe operations
- Comprehensive error handling

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/stonerjon/advanced-web-scraping-tools.git
cd advanced-web-scraping-tools
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Optional: Setup Docker Ecosystem
```bash
python docker_setup.py
```

This will create and start:
- Ollama (LLM engine)
- Open-WebUI (LLM interface)
- PostgreSQL, MongoDB, Redis
- Elasticsearch, Kibana
- Prometheus, Grafana

---

## 🚀 Quick Start

### 1. Check IP Status First (IMPORTANT!)
```bash
python main.py ip
```
**Output:**
```
🌐 IP STATUS REPORT
IP Address: 203.0.113.42
Country: United States
VPN Active: NO
Proxy Active: NO
Risk Level: ✅ LOW
```

### 2. Quick Scrape with AI Extraction
```bash
python main.py scrape "https://example.com" --schema '{"title": "string", "links": ["string"]}'
```

### 3. Full Domain Reconnaissance
```bash
python main.py recon example.com
```

### 4. Security Scanning
```bash
python main.py scan "https://example.com"
```

### 5. View Data Sources Catalog
```bash
python main.py sources

# View specific category
python main.py sources --category "Business Intelligence"
```

### 6. Launch TUI Dashboard
```bash
python main.py dashboard
```

### 7. Start Optional LLM Agent
```bash
python main.py agent
```

**Then select your mode:**
- MANUAL: Pure CLI (recommended first time)
- AUTO: Full LLM control (requires Open-WebUI running)
- HYBRID: Mixed mode

---

## 🛡️ IP Leak Protection - How It Works

### The Safety Chain:

```
┌─────────────────────────────────────────────────┐
│ 1. User initiates scrape                        │
│    python main.py scrape "https://target.com"  │
└────────────────┬────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────┐
│ 2. IP Status Check                              │
│    - Query 5 IP endpoints                       │
│    - Detect VPN/Proxy                           │
│    - Assess risk level                          │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Risk Level?    │
         └───┬────────┬──┬┘
             │        │  └─ CRITICAL/HIGH → 🛑 HALT
             │        └──── MEDIUM → ⚠️ WARN
             └───────────── LOW → ✅ PROCEED
                 │
┌─────────────────▼────────────────────────────────┐
│ 3. User Notification                            │
│    Display full IP status in rich panel         │
│    User confirms before proceeding               │
└────────────────┬────────────────────────────────┘
                 │
     ┌───────────▼──────────────┐
     │ User approves? (--no-proxy to skip)
     └───┬──────────────────────┘
         │
┌─────────▼────────────────────────────────────────┐
│ 4. Safe Scraping with Proxy Rotation            │
│    - Apply proxy to request                     │
│    - Monitor response                           │
│    - Report success/failure                     │
└─────────────────────────────────────────────────┘
```

### Enable Always-On Monitoring:

```python
from advanced_scraper.ip_leak_detector import IPLeakDetector

detector = IPLeakDetector()

# Register halt callback
def on_leak_detected(status):
    print(f"🛑 PROCESS HALTED: IP leak detected!")
    print(f"Current IP: {status.current_ip}")
    print(f"Risk: {status.risk_level.value}")

detector.register_leak_callback(on_leak_detected)
detector.start_monitoring(interval=60)  # Check every 60 seconds
```

---

## 📊 Metrics Monitoring

### Launch Full Metrics Dashboard:
```bash
python main.py dashboard
```

**Displays in Real-Time:**
- 📈 Total requests & success rate
- ⚡ Requests/sec, success/sec, errors/sec
- 🌐 Current IP & risk level
- 📦 Top data sources being used
- 💻 CPU, Memory, Disk utilization
- 🎯 Request rate analytics

### Programmatic Access:
```python
from advanced_scraper.metrics_hud import MetricsCollector, MetricsHUD

collector = MetricsCollector()
hud = MetricsHUD(collector)

# Record metrics
collector.record_request(success=True, bytes_=50000, source="hunter_io")

# Start live display
hud.start_live_display(interval=2.0)  # Updates every 2 seconds
```

---

## 🤖 Optional LLM Integration (Open-WebUI)

### Starting Autonomous Mode:

```bash
python main.py agent
```

**Choose your mode:**

#### 1. MANUAL (Recommended)
- Pure CLI control
- No LLM required
- Works offline

#### 2. AUTO (Full Autonomy)
- LLM plans entire scraping campaigns
- Autonomous decision making
- Self-optimizing

#### 3. HYBRID (Assisted)
- Get LLM suggestions
- You control execution
- Best of both worlds

### Example Autonomous Task:

```python
from advanced_scraper.openweb_ui_bridge import OpenWebUIBridge

bridge = OpenWebUIBridge()

# Define autonomous task
task = bridge.autonomous_scrape_task(
    target="techcrunch.com",
    objectives=[
        "Extract all startup news mentions",
        "Identify trending technologies",
        "Find venture capital announcements"
    ]
)

# LLM generates plan with:
# - Best data sources to use
# - Extraction patterns
# - Rate limiting strategy
# - Error handling approach
# - Result aggregation method
```

### Interactive LLM Session:

```bash
python main.py agent
# Select mode 2 (AUTO) or 3 (HYBRID)
# Start typing queries:

>>> Find me information about Python web frameworks

>>> What's the best way to scrape GitHub API?

>>> Help me plan a OSINT investigation on a domain
```

---

## 🐳 Docker Services

### Start Everything:
```bash
python docker_setup.py
```

### Service URLs & Credentials:

| Service | URL | Credentials |
|---------|-----|-------------|
| Ollama | `http://localhost:11434` | No auth |
| Open-WebUI | `http://localhost:8000` | Set password first |
| PostgreSQL | `localhost:5432` | `scraper` / `piratecove-password` |
| MongoDB | `localhost:27017` | `scraper` / `piratecove-password` |
| Redis | `localhost:6379` | No auth |
| Elasticsearch | `http://localhost:9200` | No auth |
| Kibana | `http://localhost:5601` | No auth |
| Prometheus | `http://localhost:9090` | No auth |
| Grafana | `http://localhost:3000` | `admin` / `piratecove-password` |

### Commands:
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f open-webui

# Stop services
docker-compose down

# Full reset
docker-compose down -v
```

---

## 📚 Python API Usage

### Basic Scraping
```python
from advanced_scraper.agents import ScrapingAgent

agent = ScrapingAgent(ai_provider="ollama")

result = agent.quick_scrape(
    "https://example.com",
    schema={"title": "string", "links": ["string"]}
)

print(result)
```

### With Proxy Protection
```python
from advanced_scraper.proxy_wrapper import ProxyWrapper

wrapper = ProxyWrapper()
wrapper.add_proxy("proxy1.example.com:8080")
wrapper.add_proxy("proxy2.example.com:8080")

# Check IP safety
wrapper.check_ip_status()
should_proceed, reason = wrapper.should_proceed()

if should_proceed:
    # Safe to scrape
    pass
else:
    print(f"Cannot proceed: {reason}")
```

### Using Metrics Collector
```python
from advanced_scraper.metrics_hud import MetricsCollector

collector = MetricsCollector()

# In your scraping loop
for item in scrape_results:
    success = item['status'] == 200
    bytes_scraped = len(item['data'])
    source = item['source']
    
    collector.record_request(success, bytes_scraped, source)

# Get stats
print(f"Success rate: {collector.get_success_rate()}%")
print(f"Requests/sec: {collector.get_rate(MetricType.REQUESTS)}")
```

---

## 🔒 Security Best Practices

### 1. Always Check IP First
```bash
python main.py ip
```

### 2. Use Proxy Rotation
```python
wrapper.add_proxies_from_file("proxies.txt")
```

### 3. Respect Rate Limits
```python
# Built-in adaptive rate limiting
from advanced_scraper.rate_limiter import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter()
limiter.wait()  # Waits appropriately
```

### 4. Disable IP Leak Detection Only When Necessary
```bash
# Skip IP checks (NOT RECOMMENDED)
python main.py scrape "url" --no-proxy
```

### 5. Monitor Background
```python
detector = IPLeakDetector()
detector.start_monitoring(interval=60)  # Check every 60 seconds
```

---

## 📖 Command Reference

```bash
# Core commands
python main.py scrape <url> [--schema JSON]                 # Scrape with extraction
python main.py recon <domain>                               # Full reconnaissance
python main.py scan <url>                                   # Security IOC scan

# Dashboard & monitoring
python main.py dashboard                                     # Launch TUI dashboard
python main.py ip                                            # Check IP status
python main.py sources [--category NAME]                     # View data sources

# Optional LLM
python main.py agent                                         # Start LLM agent

# Global options
--no-proxy                                                    # Disable IP leak detection
--provider [ollama|groq|openai|anthropic]                    # AI provider
```

---

## 🏗️ Architecture

### Modular Components (21+ Tools)

```
advanced_scraper/
├── agents.py                    # Unified agent interface (OPTIONAL)
├── stealth_requester.py         # TLS/HTTP2 bypass
├── auth_manager.py              # Authentication handling
├── account_automator.py         # Account creation/management
├── ai_extractor.py              # Multi-provider LLM interface
├── fast_parser.py               # HTML/DOM parsing
├── rate_limiter.py              # Adaptive rate limiting
├── streaming_sink.py            # Real-time data handling
├── header_spoofer.py            # Browser spoofing
├── lite_proxy.py                # Proxy rotation
├── subdomain_recon.py           # Subdomain discovery
├── infra_recon.py               # Infrastructure mapping
├── api_hunter.py                # API endpoint discovery
├── tech_profiler.py             # Technology detection
├── lead_extractor.py            # Email/contact extraction
├── identity_validator.py        # Data validation
├── domain_intel.py              # WHOIS/domain data
├── threat_intel.py              # Threat database integration
├── social_scoper.py             # Social media aggregation
├── state_manager.py             # Session/state persistence
├── ioc_scanner.py               # Security IOC detection
│
├── ENHANCEMENTS (NEW)
├── metrics_hud.py               # Real-time monitoring dashboard
├── ip_leak_detector.py          # 🛑 IP leak detection & prevention
├── proxy_wrapper.py             # Intelligent proxy management
├── tui_dashboard.py             # OpenCode-style TUI interface
├── openweb_ui_bridge.py         # Optional LLM automation
├── data_sources.py              # 100+ data source catalog
└── docker_setup.py              # Docker ecosystem setup
```

---

## 🎯 Development Workflow

### Stage 1: Reconnaissance
1. Run `python main.py ip` to verify connection
2. View data sources: `python main.py sources`
3. Plan your approach

### Stage 2: Configuration
1. Setup proxies (optional)
2. Configure LLM (optional)
3. Set extraction schemas

### Stage 3: Execution
1. Run scrape command
2. Monitor dashboard in real-time
3. Handle errors gracefully

### Stage 4: Analysis
1. Export metrics
2. Analyze results in Grafana
3. Iterate and improve

---

## 🤝 Contributing

This is free and open-source software. Contributions welcome!

**PirateCove Software Philosophy:**
- ✅ Free tier always available
- ✅ Open source & transparent
- ✅ No proprietary lockdown
- ✅ Community-driven development
- ✅ Production-ready from day one

---

## 📄 License

MIT License - See LICENSE file

---

## 🏴‍☠️ Credits

**Captain ShearWater Slasher's Arsenal**
- Designed for ethical OSINT, security research, and legitimate business intelligence
- Production-ready since day one
- PirateCove Software © 2024

---

## ⚠️ Legal Disclaimer

This tool is for **educational and authorized security research only**. Users are responsible for:
- Obtaining proper authorization before scraping any target
- Respecting robots.txt and terms of service
- Complying with all applicable laws and regulations
- Responsible disclosure of security vulnerabilities

**Use responsibly. Happy scraping! 🏴‍☠️**

````
