from PySimpleGUI.PySimpleGUI import No
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
# from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs

driver = webdriver.Chrome('chromedriver.exe')
driver.get('https://www.ekiten.jp/shop_70897950/')
html = driver.page_source

soup = bs(html, 'lxml')
juble_name = soup.select_one(
    'body > div.l-wrapper > div > div.l-top_contents > div.layout_media.p-topic_path_container > div.layout_media_wide > div > a:nth-child(3)'
).get_text()
tel = soup.select_one(
    'body > div:nth-child(12) > div > div.p-tel_modal_phone_number > div > div > p'
).get_text()
table_col = soup.select(
    'body > div.l-wrapper > div > div.l-contents_wrapper > main > div.p-shop_content_container.p-shop_content_container_relative > table > tbody > tr > th'
)
table_info = soup.select(
    'body > div.l-wrapper > div > div.l-contents_wrapper > main > div.p-shop_content_container.p-shop_content_container_relative > table > tbody > tr >td'
)

table_list = {}
for menu, info in zip(table_col, table_info):
    menu = menu.get_text()
    info = info.get_text()
    info = info.replace(" ", "")
    info = info.replace("　", "")
    info = info.replace("\n", "")
    info = info.replace("地図で場所を見るGoogleマップで見る", "")
    table_list[menu] = info
store_name = table_list['店舗名']
try:
    store_kana = soup.select_one('body > div.l-wrapper > div > div.l-top_contents > div.p-shop_header > div.layout_media.p-shop_header_inner > div > div.p-shop_header_name_container > div > span').get_text()
except AttributeError:
    store_kana = None
address = table_list['住所']
print(juble_name)
print(tel)
print(store_name)
print(store_kana)
print(address)
driver.quit()
