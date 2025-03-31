import requests
from bs4 import BeautifulSoup
import shodan
from packaging import version
import time
import re
import random
# Requires: pip install fpdf
from fpdf import FPDF

#  ,___  
#  {O,O}  
#  /)__)  
#  _"_"_

# Project Owl by Wayne Kenney
# WordPress scanning hacking vulnerability scanner for attack payloads

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Project Owl Security Report", ln=1, align='C')
pdf.output("security_report.pdf")

time.sleep(random.uniform(0.5, 2.5))  # Random delay between checks

CISA_API = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

class ProjectOwlScanner:
    def __init__(self, shodan_api_key=None, nvd_api_key=None):
        self.shodan_api_key = shodan_api_key
        self.nvd_api_key = nvd_api_key
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ProjectOwl/2.0'})
        self.nvd_rate_limit_delay = 6  # NVD API requires 6 seconds between requests
        
        # WordPress paths to check
        self.common_paths = [
            'wp-login.php',
            'wp-admin/',
            'wp-content/',
            'wp-includes/',
            'xmlrpc.php',
            'wp-config.php',
            'license.txt',
            'readme.html'
        ]
        
        # Known vulnerable plugins/themes database
        self.vulnerable_assets = {
            'pymntpl-paypal-woocommerce': {'path': 'wp-content/plugins/pymntpl-paypal-woocommerce/'},
            'woocommerce': {'path': 'wp-content/plugins/woocommerce/'},
            'twentytwentythree': {'path': 'wp-content/themes/twentytwentythree/'}
        }

import requests
from bs4 import BeautifulSoup
import shodan
import time
import re
import random
from fpdf import FPDF
from datetime import datetime

class ProjectOwlScanner:
    def __init__(self, shodan_api_key=None, nvd_api_key=None, stealth_mode=False):
        self.shodan_api_key = shodan_api_key
        self.nvd_api_key = nvd_api_key
        self.stealth_mode = stealth_mode
        self.report_data = []
        
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

    def stealth_delay(self):
        """Random delay to avoid detection"""
        if self.stealth_mode:
            delay = random.uniform(1.0, 3.5)
            time.sleep(delay)

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
        
        # Core scanning functions
        self.detect_version(url)
        self.detect_plugins_themes(url)
        self.enumerate_users(url)
        self.security_checks(url)
        
        # Intelligence modules
        if self.shodan_api_key:
            self.shodan_scan(url)
            
        if self.nvd_api_key:
            self.check_cisa_kev()  # Check CISA's Known Exploited Vulnerabilities
            
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

    def generate_report(self):
        """Generate PDF report of findings"""
        print("\n[*] Generating security report...")
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Report header
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Project Owl Security Report", ln=1, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ln=1, align='C')
            pdf.ln(10)
            
            # Findings
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Scan Findings:", ln=1)
            pdf.set_font("Arial", size=12)
            
            for line in self.report_data:
                pdf.multi_cell(0, 10, txt=line)
                pdf.ln(2)
            
            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, txt="Generated by Project Owl - WordPress Security Scanner", ln=1)
            
            report_filename = f"project_owl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(report_filename)
            print(f"[+] Report generated: {report_filename}")
            
        except Exception as e:
            print(f"[-] Error generating report: {str(e)}")

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
        """Enhanced security checks with debug log protection"""
        print("\n[*] Performing security checks...")
        self.report_data.append("\nSecurity Checks:")
        
        # Debug log check - with protection recommendation
        try:
            debug_log_url = f"{url}wp-content/debug.log"
            response = self.session.get(debug_log_url)
            if response.status_code == 200:
                print("[-] Found debug.log file exposed (security risk)")
                self.report_data.append("Critical: debug.log file exposed")
                
                # Provide protection steps in report
                protection_steps = [
                    "Debug Log Protection Needed:",
                    "1. Add this to your wp-config.php:",
                    "   define('WP_DEBUG', false);",
                    "   define('WP_DEBUG_LOG', false);",
                    "   define('WP_DEBUG_DISPLAY', false);",
                    "2. Delete existing debug.log file",
                    "3. Add this to your .htaccess:",
                    "   <Files debug.log>",
                    "       Order allow,deny",
                    "       Deny from all",
                    "   </Files>"
                ]
                
                for step in protection_steps:
                    self.report_data.append(step)
                    
        except Exception as e:
            pass

    def shodan_scan(self, url):
        """Use Shodan to gather additional intelligence"""
        print("\n[*] Querying Shodan for additional intelligence...")
        try:
            domain = url.split('//')[1].split('/')[0]
            api = shodan.Shodan(self.shodan_api_key)
            results = api.search(f"hostname:{domain}")
            
            print(f"[+] Shodan found {results['total']} results for {domain}")
            for result in results['matches'][:3]:
                print(f"  - IP: {result['ip_str']}")
                print(f"    Port: {result['port']}")
                print(f"    Organization: {result.get('org', 'N/A')}")
                print(f"    Banner: {result['data'][:100]}...")
                
        except Exception as e:
            print(f"[-] Shodan error: {str(e)}")

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
    scanner = ProjectOwlScanner(
        shodan_api_key="API_Key",
        nvd_api_key="API_Key",
        stealth_mode=True  # Enable stealth mode
    )
    
    target_url = input("Enter URL (https://website.com/): ")  # Always get proper authorization
    scanner.scan_without_rest_api(target_url)