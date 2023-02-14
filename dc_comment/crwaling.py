import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pprint import PrettyPrinter

# 봇 차단을 위한 헤더 설정
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua-mobile": "?0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko-KR,ko;q=0.9"
    }


pp = PrettyPrinter()

service = Service("../chromedriver.exe")
driver = webdriver.Chrome(service=service)


def get_dc_comment(url):
    driver.get(url)

    time.sleep(2)

    driver.find_element(
        by=By.CSS_SELECTOR,
        value="#container > section.left_content > article:nth-child(3) > div.list_array_option.clear > div.array_tab.left_box > button:nth-child(2)"
    ).click()

    time.sleep(2)
    posts = driver.find_elements(by=By.CSS_SELECTOR,
                                value="#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr.ub-content.us-post >  td.gall_tit.ub-word > a:nth-child(1)")

    links = [post.get_attribute("href") for post in posts]
    for i in range(len(posts)):
        post = posts[i]
        print(f"==== {post.text} ====")

        time.sleep(1.4)
        html = requests.get(links[i], headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")
        time.sleep(1)
        content = soup.select_one(
            "#container > section > article:nth-child(3) > div.view_content_wrap > div > div.inner.clear > div.writing_view_box > div.write_div"
        )
        content_txt = content.text
        comments = soup.select(
            "#focus_cmt > div.comment_wrap.show > div.comment_box > ul > li.ub-content > div > div.clear.cmt_txtbox.btn_reply_write_all > p"
        )

        print("==== 본문 내용 ====")
        print(content_txt)
        print(comments)
        print("==== 댓글 내용 ====")
        for comment in comments:
            print(comment.text)


result = get_dc_comment(url="https://gall.dcinside.com/board/lists?id=exam_new2")

pp.pprint(result)
