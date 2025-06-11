import selenium.common

from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webtools_library.cacher import Cacher
from webtools_library.general import get_logger, make_hash, closest_word


class SeleniumScrape:
    def __init__(self, headless: bool=False, *, user_id: str="", **kwargs):
        """
        headless: no browserr UI
        """
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--start-minimized")  
        self.driver = Driver(
            headless1=headless,
            uc=False,
            swiftshader=True,
            incognito=True,
            undetectable=kwargs.get("undetectable", False)
            )
        
        self.logger = get_logger(user_id, **kwargs)
        self.cacher = Cacher(**kwargs)
        self._kwargs = kwargs
    

    def open_url(self, url: str, repeat: int=0):
        self.logger.info(f"opening url {url}")
        try:
            self.driver.open(url)
        except:
            repeat+=1
            self.open_url(url, repeat)
            assert not repeat>=5, "Unable to open url after 5 attempts"


    def click_by_script(self, selector: str):
        self.driver.execute_script(f'document.querySelector("{selector}").click();')
    

    def get_webelement_objs(self, selector: str, driver=None, by: str=None):
        """
        selector: html selector e.g. div.vehicle-card in the tag <div class="vehicle-card">vehicle</div>
        """
        driver = driver or self.driver
        if not by:
            by = "css selector"
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((by, selector))
            )
        except selenium.common.exceptions.TimeoutException as e:
            return []
        except Exception as e:
            e = f"selenium {type(e).__name__}: {str(e)}"
            self.logger.warning(e)
            return []
        return driver.find_elements(by, selector)
        

    def get_webelement_text(self, selector: str, driver=None, by: str=None):
        we = self.get_webelement_objs(selector, driver, by)
        w = []
        for el in we:
            t = el.text.strip()
            if not t:
                t = el.get_attribute("textContent")
            if t:
                w.append(t)
        return w
    

    def get_webelement_table_data(self, selector: str):
        sects = self.get_webelement_objs(selector)
        results = []
        for sect in sects:
            dts = sect.find_elements(By.TAG_NAME, 'dt')
            dds = sect.find_elements(By.TAG_NAME, 'dd')

            result = {}

            for dt, dd in zip(dts, dds):
                text = dd.text.strip()
                if not text:
                    spans = dd.find_elements(By.TAG_NAME, 'span')
                    if spans:
                        text = spans[0].text.strip()
                result[dt.text.strip()] = text
            results.append(result)
        return results
    

    def quit_driver(self):
        self.driver.quit()