from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')  # GPU 사용 비활성화
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

# 크롤링할 URL (팔로워 페이지)
url = "https://www.vivino.com/users/sippingfinewine/followers"  # 실제 팔로워 페이지 URL로 변경
driver.get(url)

# 페이지 로드 대기
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='user-friend-card clearfix row']")))

# 팔로워 URL 저장 리스트
follower_urls = []

# 스크롤을 천천히 내리는 함수
def slow_scroll(driver, pause_time=1, scroll_increment=300):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_increment)
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # 더 이상 스크롤되지 않을 경우 종료
            break
        last_height = new_height

# "Show More" 버튼을 클릭하면서 팔로워 URL 크롤링 (최대 50명)
def load_and_scrape_followers(driver, max_followers=50, pause_time=2):
    while len(follower_urls) < max_followers:
        try:
            # 팔로워 목록 크롤링
            follower_cards = driver.find_elements(By.XPATH, "//div[@class='user-friend-card clearfix row']")
            for card in follower_cards:
                if len(follower_urls) >= max_followers:  # 50명 도달 시 종료
                    print(f"Collected {max_followers} follower URLs. Stopping.")
                    return
                
                try:
                    # 팔로워 URL 추출
                    follower_url = card.find_element(By.XPATH, ".//a[@class='pull-left friend-picture text-inline-block']").get_attribute("href")
                    if follower_url not in [url['profile_url'] for url in follower_urls]:  # 중복 제거
                        follower_urls.append({"profile_url": follower_url})
                except Exception:
                    continue  # URL 추출 실패 시 무시

            # 스크롤하여 "Show More" 버튼 보이게 하기
            slow_scroll(driver, pause_time=0.5, scroll_increment=300)

            # "Show More" 버튼 클릭
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@id='btn-more']"))
                )
                driver.execute_script("arguments[0].click();", show_more_button)  # JavaScript로 버튼 클릭
                time.sleep(pause_time)  # 데이터 로딩 대기
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                print(f"No more 'Show More' button found or unable to click. Stopping. Error: {e}")
                break
        except Exception as e:
            print(f"Error during scraping: {e}")
            break

# 데이터를 로드하며 크롤링
load_and_scrape_followers(driver, max_followers=50)

# 팔로워 URL 데이터를 CSV로 저장
if follower_urls:
    output_file = os.path.expanduser('./follower_urls.csv')
    df = pd.DataFrame(follower_urls)
    df.to_csv(output_file, index=False)
    print(f"Follower URLs saved to {output_file}")
else:
    print("No follower URLs found to save.")

# Selenium WebDriver 종료
driver.quit()