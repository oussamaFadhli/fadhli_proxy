from random import choice
from json import dump, load
from fadhli_proxy.source import Providers
import fadhli_proxy.cache as cache
import logging
import sys

logger = logging.getLogger("fadhli_proxy")
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]:%(message)s")
streamhandler = logging.StreamHandler(stream=sys.stdout)
streamhandler.setFormatter(logFormat)
logger.addHandler(streamhandler)


class Proxy:
    def __init__(
        self,
        countries: list = [],
        protocol: str = "http",
        maxProxies: int = 10,
        autoRotate: bool = False,
        cachePeriod: int = 10,
        cacheFolder: str = "",
        debug: bool = False,
        logToFile: bool = False,
    ):
       
        self.countries = [i.upper() for i in countries]
        self.protocol = protocol
        self.maxProxies = maxProxies
        self.autoRotate = autoRotate
        self.cachePeriod = cachePeriod
        if cacheFolder == "":
            self.cacheFilePath = ".fadhli_proxy.json"
        else:
            self.cacheFilePath = f"{cacheFolder}/.fadhli_proxy.json"
        if debug:
            logger.setLevel(logging.DEBUG)
        if logToFile:
            if cacheFolder == "":
                logFilePath = "fadhli_proxy.log"
            else:
                logFilePath = f"{cacheFolder}/fadhli_proxy.log"
            fileHandler = logging.FileHandler(logFilePath)
            fileHandler.setFormatter(logFormat)
            logger.addHandler(fileHandler)
        self.update()

    def update(self):
        try:
            with open(self.cacheFilePath, "r") as file:
                data = load(file)
                self.expiry = data[0]
                expired = cache.checkExpiry(self.expiry)
            if not expired:
                logger.info(
                    "Loaded proxies from cache",
                )
                self.proxies = data[1]
                self.expiry = data[0]
                self.current = self.proxies[0]
                return
            else:
                logger.info(
                    "Cache expired. Updating cache.",
                )
        except FileNotFoundError:
            logger.info("No cache found. Cache will be created after update")

        self.proxies = []
        for providerDict in Providers:
            if self.protocol not in providerDict["protocols"]:
                continue
            if (len(self.countries) != 0) and (not providerDict["countryFilter"]):
                continue
            self.proxies.extend(
                providerDict["provider"](self.maxProxies, self.countries, self.protocol)
            )
            if len(self.proxies) >= self.maxProxies:
                break
        if len(self.proxies) == 0:
            logger.warning(
                "No proxies found for current settings. To prevent runtime error updating the proxy list again.",
            )
            self.update()
        with open(self.cacheFilePath, "w") as file:
            self.expiry = cache.getExpiry(self.cachePeriod).isoformat()
            dump([self.expiry, self.proxies], file)
        self.current = self.proxies[0]

    def rotate(self):
       
        if cache.checkExpiry(self.expiry):
            self.update()
        self.current = choice(self.proxies)

    def proxy(self):
        
        if cache.checkExpiry(self.expiry):
            self.update()
        if self.autoRotate == True:
            return choice(self.proxies)
        else:
            return self.current
