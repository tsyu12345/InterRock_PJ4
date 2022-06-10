from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
import re
def get():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
        #browser_path = resource_path('../../bin/chrome-win/chrome.exe')
    browser_path = 'F:/ProdFolder/InterRock_PJ4/bin/chrome-win/chrome.exe'
    options.binary_location = browser_path
    driver = webdriver.Chrome(executable_path="F:/ProdFolder/InterRock_PJ4/bin/chromedriver.exe", options=options)
    sub_driver = webdriver.Chrome(executable_path="F:/ProdFolder/InterRock_PJ4/bin/chromedriver.exe", options=options)
    
    start_url = "https://www.ekiten.jp/area/a_prefecture13/" 
    
    driver.get(start_url)
    wait = WebDriverWait(driver, 20)
    wait_sub = WebDriverWait(sub_driver, 20)
    dict_list = []
    big_list = []
    #大ジャンルのリンクを取得
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.l-side_contents_search_images')))
    ul_elm = driver.find_element_by_css_selector('body > div.l-wrapper > div > div.l-contents_wrapper > div > nav > div:nth-child(2) > ul > li > div > div > div > div > div > ul')
    li_elm = ul_elm.find_elements_by_css_selector('li')
    for li in li_elm:
        big_junle_str = li.find_element_by_css_selector('a').get_attribute("href")
        big_junle_japanese = li.find_element_by_tag_name('span').get_attribute("textContent")
        big_junle_japanese = big_junle_japanese.replace("\n", "")
        big_junle_japanese = big_junle_japanese.replace(" ", "")
        big_junle_japanese = big_junle_japanese.replace("　", "")
        sub_driver.get(big_junle_str)
        big_junle_str = big_junle_str.split("/")[3]
        print("BIG GENLE: ",big_junle_str)
        print("JAPANESE BIG", big_junle_japanese)
        big_list.append(big_junle_japanese)
        #小ジャンルのリンクを取得
        genle_obj = {}
        wait_sub.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.l-side_contents_search_buttons')))
        cat_ul_elm = sub_driver.find_element_by_css_selector('ul.l-side_contents_search_buttons')
        cat_li_elm = cat_ul_elm.find_elements_by_css_selector('li')
        for li in cat_li_elm:
            
            small_junle_str = li.find_element_by_css_selector('a').get_attribute("href")
            small_junle_japanese = li.find_element_by_tag_name("span").get_attribute("textContent")
            small_junle_japanese = small_junle_japanese.replace("\n", "")
            small_junle_japanese = small_junle_japanese.replace(" ", "")
            small_junle_japanese = small_junle_japanese.replace("　", "")
            small_junle_japanese = re.sub(r"[¥(\d¥)]", "", small_junle_japanese)
            small_junle_str = small_junle_str.split("/")[3]
            

            print("SMALL GENLE", small_junle_str)
            print("JAPANESE SMALL", small_junle_japanese)
            genle_obj[small_junle_japanese] = small_junle_str
            
        dict_list.append(genle_obj)
        
    
    with open("dict.txt", "w", encoding="utf-8") as file:
        print(dict_list, file=file)
        print(big_list, file=file)
        
if __name__ == "__main__":
    get()