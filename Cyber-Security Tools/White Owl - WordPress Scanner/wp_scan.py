import requests
from bs4 import BeautifulSoup
import shodan
from packaging import version
import time
import re
import random
# Requires: pip install fpdf
from threading import Lock
from fpdf import FPDF
from colorama import Fore, Style
from colorama import init
from fpdf import FPDF
from datetime import datetime
from urllib.parse import urlparse
    
init(autoreset=True)  # Automatically resets colors after each print

#  ,___  
#  {O,O}  
#  /)__)  
#  _"_"_

# Project Owl by Wayne Kenney
# WordPress scanning hacking vulnerability scanner for attack payloads

time.sleep(random.uniform(0.5, 2.5))  # Random delay between checks

CISA_API = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

class ProjectOwlScanner:
    def __init__(self, shodan_api_key=None, nvd_api_key=None, wpvulndb_api_key=None, wpscan_api_key=None, stealth_mode=False):
        self.shodan_api_key = shodan_api_key
        self.nvd_api_key = nvd_api_key
        self.wpvulndb_api_key = wpvulndb_api_key
        self.wpscan_api_key = wpscan_api_key
        self.stealth_mode = stealth_mode
        self.report_data = []
        self.nvd_rate_limit_delay = 6  # NVD API requires 6 seconds between requests
        self.wpvulndb_lock = Lock()
        self.nvd_lock = Lock()
        self.wp_vuln_db_url = "https://wpvulndb.com/api/v3/vulnerabilities"
        self.wpscan_api_url = "https://wpscan.com/api/v3/"  # Premium (More detailed)

        self.wp_vuln_db_url = "https://wpvulndb.com/api/v3/vulnerabilities"
        self.wpscan_api_url = "https://wpscan.com/api/v3/"
        self.exploit_db_url = "https://www.exploit-db.com/search"
        self.packetstorm_url = "https://packetstormsecurity.com/search/"
        self.wpvulndb_last_call = 0
        self.wpvulndb_delay = 2  # seconds between calls
        # Initialize session with enhanced stealth headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        })
        
        self.nvd_rate_limit_delay = 6
        self.cisa_kev_url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        
        # Enhanced detection database
        self.common_paths = [
            'wp-login.php', 'wp-admin/', 'wp-content/', 'wp-includes/',
            'xmlrpc.php', 'wp-config.php', 'license.txt', 'readme.html'
        ]
        
        self.vulnerable_assets = {
            'pymntpl-paypal-woocommerce': {'path': 'wp-content/plugins/pymntpl-paypal-woocommerce/'},
            'woocommerce': {'path': 'wp-content/plugins/woocommerce/'},
            'twentytwentythree': {'path': 'wp-content/themes/twentytwentythree/'}
        }

    def validate_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        return url.rstrip('/')

    def threaded_scan(self, url, paths):
        """Use threading for faster scanning"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        print(f"\n[*] Scanning {len(paths)} paths with threading...")
        
        def check_path(path):
            try:
                full_url = f"{url}{path}"
                response = self.session.get(full_url, timeout=3)
                return (path, response.status_code)
            except:
                return (path, "Error")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_path, path) for path in paths]
            
            for future in as_completed(futures):
                path, status = future.result()
                if status == 200:
                    print(f"  [+] Found accessible: {path}")

    def check_wpvulndb(self, plugin_name, version=None):
        with self.wpvulndb_lock:
            now = time.time()
            if now - self.wpvulndb_last_call < self.wpvulndb_delay:
                time.sleep(self.wpvulndb_delay - (now - self.wpvulndb_last_call))
            self.wpvulndb_last_call = time.time()
        
        if now - self.wpvulndb_last_call < self.wpvulndb_delay:
            time.sleep(self.wpvulndb_delay - (now - self.wpvulndb_last_call))
        self.wpvulndb_last_call = time.time()
        
        print(f"\n[*] Checking WPVulnDB for {plugin_name}...")
        try:
            headers = {'Authorization': f'Token token={self.wpvulndb_api_key}'}
            response = self.session.get(f"{self.wp_vuln_db_url}/{plugin_name}", headers=headers)
            if response.status_code == 200:
                vulns = response.json()
                for vuln in vulns:
                    fixed_in = vuln.get('fixed_in')
                    if version and fixed_in and version.parse(version) < version.parse(fixed_in):
                        print(f"[!] VULNERABLE: {plugin_name} {version} < {fixed_in}")
                        self.report_data.append(f"Vulnerable: {plugin_name} {version} (fixed in {fixed_in})")

            if response.status_code == 200:
                vulns = response.json()
                print(f"[!] Found {len(vulns)} vulnerabilities in WPVulnDB")
                for vuln in vulns[:3]:  # Show top 3
                    print(f"  - {vuln.get('title', 'No title')}")
                    print(f"    Fixed in: {vuln.get('fixed_in', 'Unknown')}")
            else:
                print("[+] No vulnerabilities found in WPVulnDB")
        except Exception as e:
            print(f"[-] Error checking WPVulnDB: {str(e)}")

    def stealth_delay(self):
        """Random delay to avoid detection"""
        if self.stealth_mode:
            delay = random.uniform(1.0, 3.5)
            time.sleep(delay)

    def detect_waf(self, url):
        """Detect Web Application Firewall presence"""
        print("\n[*] Checking for WAF...")
        self.report_data.append("\nWAF Detection:")
        try:
            response = self.session.get(url, timeout=5)
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            waf_detected = None
            if 'server' in headers and 'cloudflare' in headers['server']:
                waf_detected = "Cloudflare"
            elif 'x-sucuri-id' in headers:
                waf_detected = "Sucuri"
            elif 'x-waf' in headers:
                waf_detected = "Generic WAF"
            
            if waf_detected:
                print(f"[*] WAF detected: {waf_detected}")
                self.report_data.append(f"WAF Detection: {waf_detected} detected")
            else:
                print("[+] No known WAF detected")
                self.report_data.append("WAF Detection: No known WAF detected")
                
        except requests.RequestException as e:
            print(f"[-] WAF detection failed: {str(e)}")
            self.report_data.append(f"WAF Detection: Error - {str(e)}")

    def scan_without_rest_api(self, url):
        """Enhanced scanning with new features"""
        if not url.endswith('/'):
            url += '/'
            
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report_data.append(f"Scan started at: {scan_time}")
        self.report_data.append(f"Target URL: {url}")
        
        print(f"\n[+] Starting Project Owl scan on: {url}")
        self.report_data.append("Starting Project Owl security scan")
        
        if not self.is_wordpress(url):
            print("[-] Target does not appear to be a WordPress site")
            self.report_data.append("Target verification: Not a WordPress site")
            return False
            
        print("[+] WordPress detected, beginning scan...")
        self.report_data.append("WordPress verification: Positive")
        
        # WAF detection first (affects stealth)
        self.detect_waf(url)
        
        # Core scanning
        self.detect_version(url)
        self.detect_plugins_themes(url)
        self.enumerate_users(url)
        self.security_checks(url)
        self.check_malware(url)
        
        # Intelligence modules
        if self.shodan_api_key:
            self.shodan_scan(url)
            
        if self.nvd_api_key:
            self.check_cisa_kev()
            
        # Generate report
        self.generate_report()
        
        return True

    def check_cisa_kev(self):
        """Check CISA's Known Exploited Vulnerabilities catalog"""
        print("\n[*] Checking CISA Known Exploited Vulnerabilities...")
        try:
            response = self.session.get(self.cisa_kev_url, timeout=10)
            response.raise_for_status()
            vulnerabilities = response.json()['vulnerabilities']
            
            print(f"[+] CISA KEV catalog contains {len(vulnerabilities)} entries")
            self.report_data.append(f"CISA KEV Check: {len(vulnerabilities)} known exploited vulnerabilities in catalog")
            
            # Check if any of our found plugins are in the KEV
            for vuln in vulnerabilities[:10]:  # Show top 10 for awareness
                if any(plugin.lower() in vuln.get('product', '').lower() 
                      for plugin in self.vulnerable_assets.keys()):
                    print(f"[!] CRITICAL: Known exploited vulnerability - {vuln['cveID']}")
                    print(f"    Product: {vuln['product']}")
                    print(f"    Added: {vuln['dateAdded']}")
                    self.report_data.append(
                        f"CRITICAL: Known exploited vulnerability - {vuln['cveID']} "
                        f"affecting {vuln['product']}"
                    )
                    
        except Exception as e:
            print(f"[-] Error checking CISA KEV: {str(e)}")
            self.report_data.append(f"CISA KEV Check: Error - {str(e)}")

    def check_malware(self, url):
        """Check for potential malware in wp-content/uploads/"""
        print("\n[*] Checking for malware in uploads...")
        self.report_data.append("\nMalware Scan:")
        try:
            response = self.session.get(f"{url}wp-content/uploads/", timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                suspicious_files = []
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if href.endswith('.php'):
                        suspicious_files.append(href)
                        print(f"{Fore.RED}[!]{Style.RESET_ALL} Suspicious PHP file in uploads: {href}")
                        self.report_data.append(f"CRITICAL: Suspicious PHP file in uploads: {href}")
                if not suspicious_files:
                    print("[+] No suspicious PHP files found in uploads")
                    self.report_data.append("Malware Scan: No suspicious PHP files detected")
            else:
                print("[*] Uploads directory not accessible")
                self.report_data.append("Malware Scan: Uploads directory not accessible")
        except requests.RequestException as e:
            print(f"[-] Malware check failed: {str(e)}")
            self.report_data.append(f"Malware Scan: Error - {str(e)}")

    def generate_report(self):
        """Enhanced PDF reporting with executive summary"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header with Owl ASCII
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Project Owl Security Assessment", ln=1, align='C')
            pdf.set_font("Courier", '', 10)
            pdf.multi_cell(0, 5, txt="  ,___  \n  {O,O}  \n  /)__)\n  _\"_\"_", align='C')
            pdf.ln(10)
            
            # Executive Summary
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, txt=f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
            pdf.ln(5)
            
            # Risk Summary
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Risk Summary", ln=1)
            pdf.set_font("Arial", '', 12)
            
            critical = sum(1 for line in self.report_data if "CRITICAL" in line)
            high = sum(1 for line in self.report_data if "Security Issue" in line)
            medium = sum(1 for line in self.report_data if "Security Warning" in line or "Security Note" in line)
            
            pdf.cell(200, 10, txt=f"Critical Findings: {critical}", ln=1)
            pdf.cell(200, 10, txt=f"High Risk Findings: {high}", ln=1)
            pdf.cell(200, 10, txt=f"Medium Risk Findings: {medium}", ln=1)
            pdf.ln(10)
            
            # Detailed Findings
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Detailed Findings", ln=1)
            pdf.set_font("Arial", '', 12)
            
            current_section = ""
            for line in self.report_data:
                # Section headers
                if line.startswith(("\nSecurity Checks:", "\nShodan Intelligence:")):
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(200, 10, txt=line.lstrip('\n'), ln=1)
                    current_section = line.lstrip('\n')
                    pdf.set_font("Arial", '', 12)
                    continue
                
                # Color coding
                if "CRITICAL" in line:
                    pdf.set_text_color(255, 0, 0)
                elif "Security Issue" in line:
                    pdf.set_text_color(255, 165, 0)
                elif "Security Warning" in line or "Security Note" in line:
                    pdf.set_text_color(255, 255, 0)
                else:
                    pdf.set_text_color(0, 0, 0)
                
                # Indent Shodan matches
                indent = "  " if current_section == "Shodan Intelligence:" and "Shodan Match:" in line else ""
                pdf.multi_cell(0, 10, txt=f"{indent}{line}")
                pdf.ln(2)
            
            # Remediations
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Recommended Remediations", ln=1)
            pdf.set_font("Arial", '', 12)
            
            remediations = [
                "1. Update WordPress core to latest version",
                "2. Remove or update vulnerable plugins",
                "3. Disable XML-RPC if not needed",
                "4. Implement Web Application Firewall",
                "5. Change default admin username"
            ]
            if medium > 0 and any("XML-RPC" in line for line in self.report_data):
                remediations.append("6. Add to wp-config.php: define('DISALLOW_XMLRPC', true);")
            
            for item in remediations:
                pdf.cell(200, 10, txt=item, ln=1)
            
            report_filename = f"enhanced_security_report{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(report_filename)
            print(f"[+] Report generated: {report_filename}")
            
        except Exception as e:
            print(f"[-] Error generating enhanced report: {str(e)}")
        
    def is_wordpress(self, url):
        """Check if site is WordPress"""
        for path in self.common_paths:
            try:
                response = self.session.get(f"{url}{path}", timeout=5)
                if response.status_code == 200:
                    if 'wordpress' in response.text.lower() or 'wp-' in path:
                        return True
            except:
                continue
        
        try:
            response = self.session.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_generator = soup.find('meta', attrs={'name': 'generator'})
            if meta_generator and 'wordpress' in meta_generator.get('content', '').lower():
                return True
        except:
            pass
        
        return False

    def detect_version(self, url):
        """Detect WordPress version"""
        print("\n[*] Attempting to detect WordPress version...")
        
        # Method 1: Readme.html
        try:
            response = self.session.get(f"{url}readme.html")
            if response.status_code == 200 and 'WordPress' in response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                version_text = soup.find('h1').text
                if 'WordPress' in version_text:
                    print(f"[+] WordPress version found in readme.html: {version_text}")
        except:
            pass
        
        # Method 2: Generator meta tag
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_generator = soup.find('meta', attrs={'name': 'generator'})
            if meta_generator and 'WordPress' in meta_generator.get('content', ''):
                version = meta_generator['content'].split('WordPress ')[1]
                print(f"[+] WordPress version from meta tag: {version}")
        except:
            pass
        
        # Method 3: CSS/JS files
        try:
            response = self.session.get(f"{url}wp-includes/js/wp-embed.min.js")
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if 'ver=' in line:
                        version = line.split('ver=')[1].split('"')[0]
                        print(f"[+] WordPress version from wp-embed.min.js: {version}")
                        break
        except:
            pass
        # New method: Check feed URLs
        try:
            feed = self.session.get(f"{url}feed/")
            if feed.status_code == 200:
                match = re.search(r'<generator>https://wordpress.org/\?v=([\d.]+)</generator>', feed.text)
                if match:
                    version = match.group(1)
                    print(f"[+] WordPress version from feed: {version}")
        except:
            pass
        
        # New method: Check RSD endpoint
        try:
            rsd = self.session.get(f"{url}rsd.xml")
            if rsd.status_code == 200:
                match = re.search(r'<engineName>WordPress/([\d.]+)</engineName>', rsd.text)
                if match:
                    version = match.group(1)
                    print(f"[+] WordPress version from RSD: {version}")
        except:
            pass
        try:
            return version
        except UnboundLocalError:
            return "Unknown"

    def detect_plugins_themes(self, url):
        """Detect plugins and themes"""
        print("\n[*] Scanning for plugins and themes...")
        
        # Method 1: Check common paths
        print("\n[+] Checking for common plugins:")
        for plugin, data in self.vulnerable_assets.items():
            try:
                response = self.session.get(f"{url}{data['path']}", timeout=3)
                if response.status_code == 200:
                    print(f"  [+] Found possible plugin/theme: {plugin}")
                    version = self.get_version_from_readme(f"{url}{data['path']}")
                    if version:
                        print(f"    Version: {version}")
                        if self.nvd_api_key:
                            asset_type = 'theme' if 'themes' in data['path'] else 'plugin'
                            self.check_nvd(plugin, version, asset_type)
                    if self.wpvulndb_api_key:
                        self.check_wpvulndb(plugin, version)
                    else:
                        print("    Could not determine version")
            except:
                continue
        
        # Method 2: HTML source analysis
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script') + soup.find_all('link')
            found_assets = set()
            
            for script in scripts:
                src = script.get('src', '') or script.get('href', '')
                if '/wp-content/plugins/' in src:
                    plugin_name = src.split('/wp-content/plugins/')[1].split('/')[0]
                    found_assets.add(f"plugin:{plugin_name}")
                elif '/wp-content/themes/' in src:
                    theme_name = src.split('/wp-content/themes/')[1].split('/')[0]
                    found_assets.add(f"theme:{theme_name}")
            
            if found_assets:
                print("\n[+] Found plugins/themes referenced in HTML:")
                for asset in found_assets:
                    print(f"  - {asset}")
        except:
            pass
        try:
            response = self.session.get(f"{url}wp-content/plugins/")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and not href.startswith(('?', '/', 'http')):
                        print(f"  [+] Found plugin directory: {href.rstrip('/')}")
        except:
            pass
        if self.wpscan_api_key:
            try:
                headers = {'Authorization': f'Bearer {self.wpscan_api_key}'}
                response = self.session.get(f"{self.wpscan_api_url}plugins", headers=headers)
                if response.status_code == 200:
                    plugins = response.json()
                    for plugin, data in plugins.items():
                        print(f"  [+] Found plugin via WPScan API: {plugin}")
                        if data.get('version'):
                            print(f"    Version: {data['version']}")
                            self.check_wpvulndb(plugin, data['version'])
            except Exception as e:
                print(f"[-] WPScan API error: {str(e)}")
        
        # New method: Check common plugin readme files
        common_plugins = ['akismet', 'hello', 'jetpack', 'woocommerce']
        for plugin in common_plugins:
            try:
                response = self.session.get(f"{url}wp-content/plugins/{plugin}/readme.txt")
                if response.status_code == 200:
                    print(f"  [+] Found plugin: {plugin}")
                    version = self.get_version_from_readme(response.text)
                    if version:
                        print(f"    Version: {version}")
            except:
                continue



    def enumerate_users(self, url):
        """Attempt to enumerate WordPress users"""
        print("\n[*] Attempting user enumeration...")
        
        # Method 1: Author archives
        try:
            for user_id in range(1, 10):
                response = self.session.get(f"{url}?author={user_id}", allow_redirects=False)
                if response.status_code in [301, 302]:
                    location = response.headers['location']
                    username = location.split('/')[-2] if '/' in location else location
                    print(f"[+] Found user: ID {user_id} -> {username}")
        except:
            pass
        
        # Method 2: oEmbed API
        try:
            response = self.session.get(f"{url}wp-json/oembed/1.0/embed?url={url}")
            if response.status_code == 200:
                data = response.json()
                if 'author_name' in data:
                    print(f"[+] Found author through oEmbed: {data['author_name']}")
        except:
            pass

    def security_checks(self, url):
        """Enhanced security checks with optimized vulnerability scanning"""
        print("\n[*] Performing security checks...")
        self.report_data.append("\nSecurity Checks:")
        
        # Debug.log
        try:
            debug_log_url = f"{url}wp-content/debug.log"
            response = self.session.get(debug_log_url, timeout=5)
            if response.status_code == 200:
                print(f"{Fore.RED}[!]{Style.RESET_ALL} Found debug.log at '{debug_log_url}'")
                self.report_data.append("Critical: debug.log file exposed")
                protection_steps = [
                    "Immediate Actions Required:",
                    "1. Add to wp-config.php:",
                    "   define('WP_DEBUG', false);",
                    "   define('WP_DEBUG_LOG', false);",
                    "   define('WP_DEBUG_DISPLAY', false);",
                    "2. Delete debug.log immediately",
                    "3. Add .htaccess protection:",
                    "   <Files debug.log>",
                    "       Require all denied",
                    "   </Files>"
                ]
                for step in protection_steps:
                    self.report_data.append(step)
            else:
                print(f"[+] debug.log not found (good practice)")
                self.report_data.append("Security Checks: debug.log not exposed")
        except Exception as e:
            print(f"[-] Debug log check failed: {str(e)}")
        
        # wp-config.php
        try:
            response = self.session.get(f"{url}wp-config.php")
            if response.status_code == 200 and "DB_PASSWORD" in response.text:
                print(f"{Fore.RED}[!]{Style.RESET_ALL} wp-config.php exposed!")
                self.report_data.append("CRITICAL: wp-config.php file exposed")
        except:
            pass
        
        # XML-RPC
        try:
            response = self.session.post(f"{url}xmlrpc.php", 
                                       data="<methodCall><methodName>system.listMethods</methodName></methodCall>")
            if response.status_code == 200 and "methodResponse" in response.text:
                print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} XML-RPC enabled (may be needed for plugins)")
                self.report_data.append("Security Note: XML-RPC enabled - disable via wp-config.php if unused")
        except:
            pass
        
        # Directory listing
        try:
            response = self.session.get(f"{url}wp-content/uploads/")
            if response.status_code == 200 and "Index of" in response.text:
                print(f"{Fore.RED}[!]{Style.RESET_ALL} Directory listing enabled at wp-content/uploads/")
                self.report_data.append("Security Issue: Directory listing enabled")
        except:
            pass
        
        # Plugin vuln checks
        if self.wpvulndb_api_key:
            print("\n[*] Scanning WordPress vulnerability databases...")
            for plugin_name, plugin_data in self.vulnerable_assets.items():
                print(f"  [→] Checking {plugin_name}...")
                try:
                    self.check_wpvulndb(plugin_name)
                except Exception as e:
                    print(f"  [!] Plugin check failed for {plugin_name}: {str(e)}")
        else:
            print("[*] WP VulnDB API key not configured - skipping plugin checks")

    def shodan_scan(self, url):
        """Use Shodan to gather additional intelligence"""
        print("\n[*] Querying Shodan for additional intelligence...")
        self.report_data.append("\nShodan Intelligence:")
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            api = shodan.Shodan(self.shodan_api_key)
            query = f"hostname:{domain} wordpress"
            results = api.search(query)
            print(f"[+] Shodan found {results['total']} results for {domain}")
            self.report_data.append(f"Shodan Results: Found {results['total']} matches for {domain}")
            
            if results['total'] == 0:
                print("[*] No Shodan results - trying IP-based search...")
                self.report_data.append("No hostname matches - attempting IP-based search")
                import socket
                try:
                    ip = socket.gethostbyname(domain)
                    results = api.search(f"ip:{ip} wordpress")
                    print(f"[+] Shodan found {results['total']} results for IP {ip}")
                    self.report_data.append(f"Shodan IP Search: Found {results['total']} matches for IP {ip}")
                except socket.gaierror:
                    print("[-] Could not resolve domain to IP")
                    self.report_data.append("Shodan IP Search: Failed to resolve domain")
                    return
            
            for result in results['matches'][:5]:  # Limit to 5 for brevity
                ip_port = f"IP: {result['ip_str']}, Port: {result['port']}"
                print(f"  - {ip_port}")
                self.report_data.append(f"Shodan Match: {ip_port}")
                if 'org' in result:
                    print(f"    Organization: {result.get('org', 'N/A')}")
                    self.report_data.append(f"Organization: {result.get('org', 'N/A')}")
                if 'data' in result:
                    banner = result['data'][:100].replace('\n', ' ')
                    print(f"    Banner: {banner}...")
                    self.report_data.append(f"Banner: {banner}...")
                    
        except shodan.APIError as e:
            print(f"[-] Shodan API error: {str(e)}")
            self.report_data.append(f"Shodan Error: API error - {str(e)}")
        except Exception as e:
            print(f"[-] Shodan scan error: {str(e)}")
            self.report_data.append(f"Shodan Error: {str(e)}")
            
    def check_nvd(self, asset_name, asset_version, asset_type='plugin'):
        """Check NVD for known vulnerabilities"""
        print(f"\n[*] Checking NVD for {asset_type} {asset_name} version {asset_version}...")
        
        cpe_name = asset_name.lower().replace(' ', '_')
        cpe_string = f"cpe:2.3:a:{cpe_name}:{cpe_name}:{asset_version}:*:*:*:*:wordpress:*:*"
        
        headers = {"apiKey": self.nvd_api_key} if self.nvd_api_key else {}
        
        try:
            nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {'cpeName': cpe_string, 'resultsPerPage': 20}
            
            time.sleep(self.nvd_rate_limit_delay)
            response = self.session.get(nvd_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            vulns = data.get('vulnerabilities', [])
            
            if not vulns:
                print(f"[+] No known vulnerabilities found for {asset_name} {asset_version}")
                return
            
            print(f"[!] Found {len(vulns)} potential vulnerabilities:")
            for vuln in vulns[:5]:
                cve_data = vuln.get('cve', {})
                cve_id = cve_data.get('id', 'CVE-UNKNOWN')
                
                descriptions = [desc['value'] for desc in cve_data.get('descriptions', []) 
                              if desc['lang'] == 'en']
                description = descriptions[0] if descriptions else "No description available"
                
                metrics = cve_data.get('metrics', {})
                cvss_metrics = metrics.get('cvssMetricV31', metrics.get('cvssMetricV30', [{}]))[0]
                cvss_data = cvss_metrics.get('cvssData', {})
                base_score = cvss_data.get('baseScore', 'N/A')
                severity = cvss_data.get('baseSeverity', 'N/A')
                
                print(f"\n  - {cve_id} (CVSS: {base_score}, {severity})")
                print(f"    {description[:200]}...")
                
                if 'references' in cve_data:
                    refs = [ref['url'] for ref in cve_data['references']]
                    print(f"    References: {', '.join(refs[:2])}...")
            
            if len(vulns) > 5:
                print(f"\n[!] {len(vulns)-5} additional vulnerabilities not shown...")
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Error querying NVD API: {str(e)}")
        except Exception as e:
            print(f"[-] Error processing NVD data: {str(e)}")

    def get_version_from_readme(self, base_url):
        """Extract version from readme.txt"""
        try:
            readme = self.session.get(f"{base_url}readme.txt", timeout=3)
            if readme.status_code == 200:
                version_match = re.search(r'^stable tag:\s*([\d.]+)', readme.text, re.MULTILINE | re.IGNORECASE)
                if version_match:
                    return version_match.group(1).strip()
                
                version_match = re.search(r'^version:\s*([\d.]+)', readme.text, re.MULTILINE | re.IGNORECASE)
                if version_match:
                    return version_match.group(1).strip()
        except:
            return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    scanner = ProjectOwlScanner(
        shodan_api_key="key_#1",
        nvd_api_key="key_#2",
        wpvulndb_api_key="key_#3",
        wpscan_api_key='key_#4',
        stealth_mode=True  # Enable stealth mode
    )
    
    target_url = input("Enter URL (https://website.com/): ")  # Always get proper authorization
    scanner.scan_without_rest_api(target_url)