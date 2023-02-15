import os
import networkx as nx
import time
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pprint import PrettyPrinter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

pp = PrettyPrinter()

service = Service("./chromedriver.exe")
driver = webdriver.Chrome(service=service)


def scroll_full_down():
    prev_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        current_height = driver.execute_script("return document.body.scrollHeight")

        if prev_height == current_height:
            break

        prev_height = current_height

    time.sleep(2)

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

    result = {toon: {} for toon in toon_list}
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

        result[toon] = {name.text: [] for name in episode}

        for i in range(2):
            plt.rc('font', family="Malgun Gothic")
            plt.title("댓글 네트워크 sample")

            comment_graph = nx.Graph()
            name = episode[i].text
            print(f"=== {name} 댓글 ===")
            episode[i].click()
            scroll_full_down()  # 셀레니움으로 페이지 전체 데이터를 가져오기 위해서 스크롤을 아래까지 쭉 내림 (근데 없어도 될 수도?)
            driver.switch_to.frame("commentIframe")
            # driver.find_element(
            #     by=By.CSS_SELECTOR,
            #     value="#cbox_module_wai_u_cbox_sort_option_tab2").click()

            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # 대댓글 li들을 찾기위한 elements
            li = driver.find_elements(
                by=By.CSS_SELECTOR,
                value="#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li"
            )

            # 각각 댓글의 유저 식별과 내용, 좋아요 수, 나빠요 수를 순서대로 가지고 있는 리스트
            user_names = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_info"
            )
            comments = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_text_wrap > span.u_cbox_contents"
            )
            goods = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div.u_cbox_recomm_set > a.u_cbox_btn_recomm"
            )

            bads = soup.select(
                "#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div.u_cbox_recomm_set > a.u_cbox_btn_unrecomm"
            )

            # 답글 버튼 모두 클릭
            for j in range(len(li)):
                li[j].find_element(
                    by=By.CSS_SELECTOR,
                    value="li > div.u_cbox_comment_box > div > div.u_cbox_tool > a"
                ).click()
                time.sleep(1)

            time.sleep(2)
            li = driver.find_elements(
                by=By.CSS_SELECTOR,
                value="#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li > div.u_cbox_reply_area"
            )
            for j, (user_name, comment, good, bad) in enumerate(zip(user_names, comments, goods, bads)):
                time.sleep(5)
                reply_comments = li[j].find_elements(
                    by=By.CSS_SELECTOR,
                    value="div.u_cbox_reply_area > ul.u_cbox_list > li"
                )

                print("reply comments 1:", reply_comments)
                try:
                    reply_users = [
                        reply.find_element(
                            by=By.CSS_SELECTOR,
                            value="li > div > div > div.u_cbox_info").text for reply in
                        reply_comments]

                    reply_comments = [
                        reply.find_element(
                            by=By.CSS_SELECTOR,
                            value="li > div > div > div.u_cbox_text_wrap > span.u_cbox_contents").text for reply in
                        reply_comments]

                except:
                    continue

                comment_user = user_name.text.split("옵션")[0]
                comment_graph.add_node(comment_user, content=comment.text, type="comment")
                for reply_user, reply_comment in zip(reply_users, reply_comments):
                    reply_user = reply_user.split("옵션")[0].replace("\n", "")
                    comment_graph.add_edge(
                        comment_user,
                        reply_user
                    )

                    comment_graph.nodes[reply_user]["content"] = reply_comment
                    comment_graph.nodes[reply_user]["type"] = "reply_comment"

                    print("reply user:", reply_user)
                print("reply comments 2:", reply_comments)

            nx.draw(comment_graph, pos=nx.spring_layout(comment_graph))
            nx.draw_networkx_labels(comment_graph, font_family="Malgun Gothic", pos=nx.spring_layout(comment_graph))

            plt.show()
            result[toon][name].append(comment_graph)

            pp.pprint(result[toon])  # 그래프가 잘 저장 되었는지 확인하기 위해서 print 찍어줌

            driver.back()
            episode = driver.find_elements(by=By.CSS_SELECTOR,
                                           value="#content > table > tbody > tr > td.title > a")
            time.sleep(2)


        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

    return result

webtoon_graphDict = get_webtoon_comment(url="https://comic.naver.com/webtoon/weekday")

with open("./webtoon_graph.pkl", "wb") as f:
    pickle.dump(webtoon_graphDict, f)

