"""
ONE-CLICK PoC GENERATOR - Instant exploit reproduction
Generates ready-to-use PoC commands for every finding.
"""
from typing import Dict
import urllib.parse


class PoCGenerator:
    """
    Generates one-click PoC commands for instant exploit reproduction.
    """
    
    def generate_curl_poc(self, finding: Dict) -> str:
        """
        Generate curl command PoC.
        
        Args:
            finding: Vulnerability finding dictionary
            
        Returns:
            curl command string
        """
        endpoint = finding.get('endpoint', '')
        parameter = finding.get('parameter', '')
        payload = finding.get('payload', '')
        method = finding.get('method', 'GET')
        
        if method.upper() == 'GET':
            # URL encode payload
            encoded_payload = urllib.parse.quote(payload)
            if '?' in endpoint:
                url = f"{endpoint}&{parameter}={encoded_payload}"
            else:
                url = f"{endpoint}?{parameter}={encoded_payload}"
            return f"curl -X GET '{url}'"
        else:
            # POST request
            encoded_payload = urllib.parse.quote(payload)
            return f"curl -X POST '{endpoint}' -d '{parameter}={encoded_payload}'"
    
    def generate_python_poc(self, finding: Dict) -> str:
        """Generate Python requests PoC."""
        endpoint = finding.get('endpoint', '')
        parameter = finding.get('parameter', '')
        payload = finding.get('payload', '')
        method = finding.get('method', 'GET')
        
        if method.upper() == 'GET':
            import urllib.parse
            encoded_payload = urllib.parse.quote(payload)
            if '?' in endpoint:
                url = f"{endpoint}&{parameter}={encoded_payload}"
            else:
                url = f"{endpoint}?{parameter}={encoded_payload}"
            return f"""import requests
url = '{url}'
response = requests.get(url)
print(response.text)"""
        else:
            return f"""import requests
url = '{endpoint}'
data = {{'{parameter}': '{payload}'}}
response = requests.post(url, data=data)
print(response.text)"""
    
    def generate_burp_poc(self, finding: Dict) -> str:
        """Generate Burp Suite request PoC."""
        endpoint = finding.get('endpoint', '')
        parameter = finding.get('parameter', '')
        payload = finding.get('payload', '')
        method = finding.get('method', 'GET')
        
        if method.upper() == 'GET':
            import urllib.parse
            encoded_payload = urllib.parse.quote(payload)
            if '?' in endpoint:
                url = f"{endpoint}&{parameter}={encoded_payload}"
            else:
                url = f"{endpoint}?{parameter}={encoded_payload}"
            return f"{method} {url} HTTP/1.1\nHost: {urllib.parse.urlparse(endpoint).netloc}\n"
        else:
            import urllib.parse
            encoded_payload = urllib.parse.quote(payload)
            return f"""POST {endpoint} HTTP/1.1
Host: {urllib.parse.urlparse(endpoint).netloc}
Content-Type: application/x-www-form-urlencoded
Content-Length: {len(parameter) + len(encoded_payload) + 1}

{parameter}={encoded_payload}"""
    
    def generate_all_pocs(self, finding: Dict) -> Dict[str, str]:
        """Generate all PoC formats."""
        return {
            'curl': self.generate_curl_poc(finding),
            'python': self.generate_python_poc(finding),
            'burp': self.generate_burp_poc(finding)
        }
