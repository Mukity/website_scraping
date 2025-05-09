from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import urllib.parse as urlparse
from urllib.parse import parse_qs

from webtools_library.general import get_logger


class SeleniumScrape:
    def __init__(self, headless: bool=True, *, user_id: str="", **kwargs):
        """
        headless: no browserr UI
        """
        self.driver = Driver(
            headless1=headless,
            uc=False,
            swiftshader=True,
            incognito=True
            )
        
        self.logger = get_logger(user_id, **kwargs)
    

    def open_url(self, url: str):
        self.driver.open(url)


    def _get_page_no(self, url: str, page_key: str):
        parsed = urlparse.urlparse(url)
        query_params = parse_qs(parsed.query)
        return int(query_params.get(page_key, [1])[0])

    def navigate_next_page(self, url: str, page_key: str="page"):
        if page_key not in url:
            return
        
        parsed = urlparse.urlparse(url)
        query_params = parse_qs(parsed.query)
        curr_page = int(query_params.get(page_key, [1])[0])
        nxt_page = curr_page+1
        query_params[page_key] = [str(nxt_page)]
        new_query = urlparse.urlencode(query_params, doseq=True)
        url =  f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        self.open_url(url)
        url_ = self.driver.current_url
        return url_, self._get_page_no(url_, page_key)


    def generate_page_urls(self, url: str, page_key: str="page"):
        all_urls = [url]
        url_, page_no = self.navigate_next_page(url, page_key)
        all_urls.append(url_)

        while True:
            url_, pg_no = self.navigate_next_page(url_, page_key)
            if pg_no==page_no:
                break

            page_no=pg_no
            all_urls.append(url_)
        return list(set(all_urls))


    def get_page_source(self, url: str):
        self.open_url(url)
        source = self.driver.page_source
        self.quit_driver()
        return source
    

    def get_webelement_data(self, selector: str, *, return_webelement: bool=True):
        """
        selector: html selector e.g. div.vehicle-card in the tag <div class="vehicle-card">vehicle</div>
        """
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )
        we =  self.driver.find_elements(By.CSS_SELECTOR, selector)
        if return_webelement:
            return we
        
        w = []
        for el in we:
            t = el.text
            if t.strip():
                w.append(t)
        return w


    def get_webelement_table_data(self, selector: str):
        sects = self.get_webelement_data(selector)
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