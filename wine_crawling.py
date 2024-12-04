import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')  # GPU 사용 비활성화
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

# 크롤링할 URL
url = "https://www.vivino.com/users/sippingfinewine"  # 실제 URL로 변경
driver.get(url)

# 페이지 로드 대기
time.sleep(3)

# 사용자 이름 가져오기 (xpath를 사용)
try:
    user_name = driver.find_element(By.XPATH, "//div[@class='user-header__name header-medium bold']").text.strip()
except Exception as e:
    print("User name not found")
    user_name = "Unknown User"

# 와인 평가 데이터를 저장할 리스트
wine_ratings = []

# "Show More" 버튼을 클릭하면서 데이터 크롤링
def load_and_scrape(driver, user_name, pause_time=2):
    while True:
        # 와인 평가 데이터 크롤링
        try:
            wine_cards = driver.find_elements(By.XPATH, "//div[@class='user-activity-item']")  # 각 와인 평가 데이터를 담은 div
            for wine_card in wine_cards:
                try:
                    # 와인 이름
                    wine_name = wine_card.find_element(By.XPATH, ".//p[@class='wine-name header-medium']/a").text.strip()
                    wine_name = 
                    
                    # 사용자 평가 점수 (별의 갯수)
                    user_rating_stars = wine_card.find_elements(By.XPATH, ".//span[@class='rating rating-xs text-inline-block']/i[contains(@class, 'icon-100-pct')]")
                    user_rating = len(user_rating_stars)  # 'icon-100-pct' 클래스의 개수

                    # 평균 평점
                    try:
                        avg_rating = wine_card.find_element(By.XPATH, ".//span[@class='header-large text-block']").text.strip()
                    except Exception:
                        avg_rating = "N/A"

                    # 평가 데이터 저장
                    wine_ratings.append({
                        "user_name": user_name,
                        "wine_name": wine_name,
                        "user_rating": user_rating,
                        "avg_rating": avg_rating
                    })
                except Exception as e:
                    continue  # 데이터가 없으면 무시
        except Exception as e:
            print("No wine cards found.")
            break  # 더 이상 데이터를 찾을 수 없으면 종료

        # "Show More" 버튼 클릭
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[@id='btn-more-activities']")  # "Show More" 버튼
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)  # 버튼으로 스크롤
            time.sleep(1)  # 스크롤 후 대기
            show_more_button.click()  # 버튼 클릭
            time.sleep(pause_time)  # 데이터 로딩 대기
        except Exception as e:
            print("No more 'Show More' button found or unable to click. Stopping.")
            break  # 버튼이 없으면 크롤링 종료

# 데이터를 로드하며 크롤링
load_and_scrape(driver, user_name)

# 데이터를 CSV로 저장
if wine_ratings:
    output_file = os.path.expanduser("~/vivino_wine_ratings.csv")  # 저장 파일 경로
    df = pd.DataFrame(wine_ratings)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
else:
    print("No data to save.")

# Selenium WebDriver 종료
driver.quit()
