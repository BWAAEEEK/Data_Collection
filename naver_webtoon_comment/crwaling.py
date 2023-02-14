import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pprint import PrettyPrinter
import pandas as pd
import os
import re

pp = PrettyPrinter()

service = Service("../chromedriver.exe")
driver = webdriver.Chrome(service=service)


def get_webtoon_comment(url):
    driver.get(url)

    time.sleep(2)

    toon_list = driver.find_elements(
        by=By.CSS_SELECTOR,
        value="#recommandWebtoonRank > li"
    )

    driver.find_element(
        by=By.CSS_SELECTOR,
        value="#recommandWebtoonRankWTabOver > a"
    ).click()

    time.sleep(2)
    toon_list += driver.find_elements(
        by=By.CSS_SELECTOR,
        value="#recommandWebtoonRank > li"
    )

    toon_list = set([toon.text.split("\n")[0] for toon in toon_list])

    for toon in toon_list:
        try:
            os.mkdir("./output/" + toon)
        except:
            pass
        driver.execute_script('window.open("https://google.com");')
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])

        driver.get("https://comic.naver.com/search?keyword=" + toon)

        time.sleep(2)
        driver.find_element(
            by=By.CSS_SELECTOR,
            value="#content > div:nth-child(2) > ul > li:nth-child(1) > h5 > a"
        ).click()

        time.sleep(2)
        episode = driver.find_elements(by=By.CSS_SELECTOR,
                                       value="#content > table > tbody > tr > td.title > a")

        episode_dict = {name.text: {
            "comment": [],
            "good": [],
            "bad": []
        } for name in episode}


        for i in range(2):
            name = episode[i].text
            print(f"=== {name} 댓글 ===")
            episode[i].click()
            driver.switch_to.frame("commentIframe")
            driver.find_element(
                by=By.CSS_SELECTOR,
                value="#cbox_module_wai_u_cbox_sort_option_tab2").click()

            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            comments = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_text_wrap > span.u_cbox_contents"
            )
            goods = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div.u_cbox_recomm_set > a.u_cbox_btn_recomm"
            )

            bads = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div.u_cbox_recomm_set > a.u_cbox_btn_unrecomm"
            )
            time.sleep(2)
            for comment, good, bad in zip(comments, goods, bads):
                print(f"{comment.text} | 좋아요: {good.text[3:]} | 싫어요: {bad.text[3:]}")
                episode_dict[name]["comment"].append(comment.text)
                episode_dict[name]["good"].append(good.text[3:])
                episode_dict[name]["bad"].append(bad.text[3:])

            driver.back()
            episode = driver.find_elements(by=By.CSS_SELECTOR,
                                           value="#content > table > tbody > tr > td.title > a")
            time.sleep(2)

        for name, info_dict in episode_dict.items():
            df = pd.DataFrame(info_dict)

            print(df.head(5))

            df.to_csv("./output/%s/%s.csv" % (toon, re.sub(r'[^\w\s]', '', name)), encoding="utf-8-sig")

        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)


get_webtoon_comment(url="https://comic.naver.com/webtoon/weekday")
