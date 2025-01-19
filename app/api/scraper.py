from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from typing import List
import threading
import asyncio
import re

router = APIRouter()

# Modelo de entrada
class ScraperRequest(BaseModel):
    urls: List[str]

# Función para limpiar texto
def clean_text(text):
    return re.sub(r'[\\|\\n\\*\\t\\s_(\\u2014\\u00d7#%\\u2013\\u00a9\\ud83d\\udd53\\u2582\\ud83c\\udfcd\\ufe0f\\ud83d\\udd73\\u2022\\u00ae\\xb7\\u2715),;-]+', ' ', text)

# Spider de Scrapy
class MySpider(scrapy.Spider):
    name = "fastapi_spider"

    def __init__(self, urls, result_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        self.result_dict = result_dict

    def parse(self, response):
        visible_content = response.css('body *:not(style):not(script)::text').getall()
        cleaned_content = [clean_text(content.strip()) for content in visible_content if content.strip()]
        self.result_dict[response.url] = " ".join(cleaned_content)

# Inicialización del CrawlerRunner
runner = CrawlerRunner()
twisted_thread = None

# Función para iniciar el reactor en un hilo separado
def start_reactor():
    global twisted_thread
    if not twisted_thread or not twisted_thread.is_alive():
        twisted_thread = threading.Thread(target=reactor.run, kwargs={"installSignalHandlers": False})
        twisted_thread.daemon = True
        twisted_thread.start()

# Función para ejecutar el Spider
def run_spider(urls):
    result_dict = {}
    deferred = defer.Deferred()

    @defer.inlineCallbacks
    def _crawl():
        try:
            yield runner.crawl(MySpider, urls=urls, result_dict=result_dict)
            deferred.callback(result_dict)
        except Exception as e:
            deferred.errback(e)

    reactor.callFromThread(_crawl)
    return deferred

# Convertir Deferred de Twisted en asyncio.Future
def deferred_to_future(d):
    future = asyncio.Future()

    def callback(result):
        if not future.cancelled():
            future.set_result(result)

    def errback(error):
        if not future.cancelled():
            future.set_exception(error)

    d.addCallbacks(callback, errback)
    return future

# Endpoint para scraping
@router.post("/scrape")
async def scrape(request: ScraperRequest):
    try:
        start_reactor()  # Asegurarse de que el reactor está en ejecución
        deferred = run_spider(request.urls)
        scraped_data = await deferred_to_future(deferred)
        return {"data": scraped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
