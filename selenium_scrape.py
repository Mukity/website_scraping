import json
import Levenshtein
import selenium.common

from typing import Callable, Iterable
from hashlib import md5
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import urllib.parse as urlparse
from urllib.parse import parse_qs
from redis import Redis

from webtools_library.general import get_logger

import spacy
nlp = spacy.load("en_core_web_sm")


def make_hash(val: str):
    return md5(val.encode()).hexdigest()


def similarity_score(w1: str, w2: str):
    token1 = nlp.vocab[w1]
    token2 = nlp.vocab[w2]
    if not token1.has_vector or not token2.has_vector:
        semantic = 0
    else:
        semantic = token1.similarity(token2)  # 0 to 1

    spelling = 1 - Levenshtein.distance(w1, w2) / max(len(w1), len(w2))

    return 0.6 * semantic + 0.4 * spelling


def closest_word(word: str, options: Iterable):
    return max(options, key=lambda w: similarity_score(word, w))


class Cacher:
    def __init__(self, host: str='localhost', port: str=6379, **kwargs):
        self._redis = Redis(host=host, port=port, decode_responses=True)
    

    def set(self, key: str, value: any):
        self._redis.set(key, json.dumps(value or {}))


    def get(self, key: str):
        x = self._redis.get(key)
        if x:
            return json.loads(x)


    def hset(self, name: str, key: str, value: any):
        self._redis.hset(name, key, json.dumps(value or {}))


    def hget(self, name: str, key: str):
        x = self._redis.hget(name, key)
        if x:
            return json.loads(x)

    
    def exists(self, key: str):
        return self._redis.exists(key)


    def hexists(self, name: str, key: str):
        return self._redis.hexists(name, key)


    def hset_exec(self, *, name: str, key: str, func: Callable, desc: str, logger, _cached: bool=True, **kwargs):
        vals = self.hget(name, key)
        if _cached and self.hexists(name, key):
            logger.info(f"got {desc} from cache")
        else:
            vals = func(**kwargs)
            if isinstance(vals, set):
                vals = list(vals)
            self.hset(name, key, vals)
        return vals


    def set_exec(self, *, key: str, func: Callable, desc: str, logger, _cached: bool=True,  **kwargs):
        vals = self.get(key)
        if _cached and self.exists(key):
            logger.info(f"got {desc} from cache")
        else:
            vals = func(**kwargs)
            if isinstance(vals, set):
                vals = list(vals)
            self.set(key, vals)
        return vals



class SeleniumScrape:
    def __init__(self, headless: bool=False, *, user_id: str="", **kwargs):
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
        self.cacher = Cacher(**kwargs)
    

    def open_url(self, url: str, repeat: int=0):
        self.logger.info(f"opening url {url}")
        try:
            self.driver.open(url)
        except:
            repeat+=1
            self.open_url(url, repeat)
            assert not repeat>=5, "Unable to open url after 5 attempts"


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
    

    def click_by_script(self, selector: str):
        self.driver.execute_script(f'document.querySelector("{selector}").click();')
    

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
    

    def get_webelement_objs(self, selector: str, driver=None):
        """
        selector: html selector e.g. div.vehicle-card in the tag <div class="vehicle-card">vehicle</div>
        """
        driver = driver or self.driver
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
        except selenium.common.exceptions.TimeoutException as e:
            return []
        except Exception as e:
            e = f"selenium {type(e).__name__}: {str(e)}"
            self.logger.warning(e)
            return []
        return driver.find_elements(By.CSS_SELECTOR, selector)
        

    def get_webelement_text(self, selector: str, driver=None):
        we = self.get_webelement_objs(selector, driver)
        w = []
        for el in we:
            t = el.text
            if t.strip():
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