from requests import get
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional
from datetime import datetime


def checkProxy(proxy: Tuple[str, str]) -> bool:
    """
    Check if a proxy is working by testing multiple endpoints and validating responses.
    
    Args:
        proxy: Tuple containing (proxy_address, proxy_type)
    Returns:
        bool: True if proxy is working, False otherwise
    """
    test_urls = [
        "https://checkip.amazonaws.com",
        "https://api.ipify.org",
        "https://ifconfig.me/ip"
        "https://icanhazip.com",
        "https://ident.me",
        "https://ipinfo.io/ip",

    ]
    
    proxyDict = {proxy[1]: proxy[0]}
    success_count = 0
    
    def test_url(url: str) -> Optional[bool]:
        try:
            resp = get(url, 
                      proxies=proxyDict, 
                      timeout=5,
                      headers={'User-Agent': 'Mozilla/5.0'})
            
            if resp.status_code == 200:
                # Validate IP format in response
                ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                if re.match(ip_pattern, resp.text.strip()):
                    return True
            return False
        except Exception:
            return False

    # Test multiple endpoints concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(test_url, url): url for url in test_urls}
        for future in as_completed(future_to_url):
            if future.result():
                success_count += 1

    # Consider proxy valid if at least 4 endpoints succeed
    return success_count >= 4


def log(level, message):
    level = level.upper()
    print(
        f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - [swiftshadow] - {level} : {message}'
    )
