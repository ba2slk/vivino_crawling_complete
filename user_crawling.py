from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL 및 브라우저 설정
SIPPING_FINE_WINE = "https://www.vivino.com/users/sippingfinewine/followers"
PAUSE_TIME = 3  # 데이터 로딩 대기 시간
SCROLL_INCREMENT = 300  # 스크롤 이동 크기


def setup_driver():
    """
    Chrome WebDriver를 설정하고 초기화하는 함수
    """
    options = Options()
    options.add_experimental_option("detach", True)  # 브라우저가 종료되지 않도록 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def scroll_down(driver, increment=SCROLL_INCREMENT):
    """
    페이지를 스크롤 다운하는 함수
    """
    last_height = driver.execute_script("return window.scrollY")
    new_height = last_height + increment
    driver.execute_script(f"window.scrollTo(0, {new_height});")
    time.sleep(PAUSE_TIME)
    return new_height


def click_show_more(driver):
    """
    "Show More" 버튼을 클릭하는 함수
    """
    try:
        # 버튼이 로드될 때까지 대기
        wait = WebDriverWait(driver, 5)
        show_more_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-more")))
        if show_more_button:
            print("show more button found")
        else:
            print("button not found")
        driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
        time.sleep(1)
        show_more_button.click()
        time.sleep(PAUSE_TIME)
        return True
    except Exception as e:
        print(f"No more 'Show More' button found or unable to click. Error: {e}")
        return False


def extract_user_ids(driver, collected_users):
    """
    페이지에서 User ID를 추출하는 함수
    """
    user_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/users/') and not(contains(@href, 'followers'))]")
    for user_element in user_elements:
        user_id = user_element.get_attribute("href").split("/users/")[-1]  # URL에서 User ID 추출
        if user_id:
            collected_users.add(user_id)


def collect_user_ids():
    """
    전체 프로세스를 실행하여 User ID를 수집하는 메인 함수
    """
    driver = setup_driver()
    driver.get(SIPPING_FINE_WINE)

    collected_users = set()  # 중복 방지를 위해 set 사용

    while True:
        try:
            # 1. User ID 획득
            extract_user_ids(driver, collected_users)

            # 2. 스크롤
            new_height = scroll_down(driver)

            # 3. "Show More" 버튼 클릭 (페이지 끝 도달 시)
            if new_height >= driver.execute_script("return document.body.scrollHeight"):
                if not click_show_more(driver):
                    break

        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            break

    # 수집된 User ID 출력
    print(f"Collected {len(collected_users)} user IDs:")
    for user_id in collected_users:
        print(user_id)

    driver.quit()


if __name__ == "__main__":
    try:
        collect_user_ids()
    except Exception as e:
        print(f"An error occurred: {e}")
