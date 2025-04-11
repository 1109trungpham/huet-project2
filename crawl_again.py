from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import re
import random

def crawl_again(path_to_data):
    df = pd.read_csv(path_to_data)
    for i, jobl in enumerate(df['Link công việc']):
        if isinstance(df.loc[i, 'Khu vực'], float):
            driver = webdriver.Chrome()
            try:
                driver.get(jobl)
                driver.implicitly_wait(5)

                # Mức lương - Địa điểm - Kinh nghiệm
                try:
                    job_info = driver.find_elements(By.CLASS_NAME, "job-detail__info--section-content-value")
                    salary = job_info[0].text if len(job_info) > 0 else "N/A"
                    location = job_info[1].text if len(job_info) > 1 else "N/A"
                    experience = job_info[2].text if len(job_info) > 2 else "N/A"
                except Exception as e:
                    print(f"[WARN] Lỗi job info tại {i}: {e}")
                    salary = location = experience = "N/A"

                df.loc[i, 'Khu vực'] = location
                df.loc[i, 'Kinh nghiệm'] = experience
                df.loc[i, 'Thu nhập'] = salary

                # Chi tiết tuyển dụng
                try:
                    names_left = driver.find_elements(By.CLASS_NAME, "job-description__item")
                    list_name_left = [name.get_attribute("textContent").strip().split('\n')[0] for name in names_left]
                    info_left = driver.find_elements(By.CLASS_NAME, "job-description__item--content")

                    for j in range(min(len(list_name_left), len(info_left))):
                        if list_name_left[j] == "Cách thức ứng tuyển":
                            break
                        df.loc[i, list_name_left[j]] = info_left[j].text
                except Exception as e:
                    print(f"[WARN] Lỗi chi tiết tuyển dụng tại {i}: {e}")

                # Thông tin chung
                try:
                    name_right = driver.find_elements(By.CLASS_NAME, "box-general-group-info-title")
                    list_name_right = [name.text for name in name_right]
                    info_right = driver.find_elements(By.CLASS_NAME, "box-general-group-info-value")

                    for j in range(min(len(list_name_right), len(info_right))):
                        df.loc[i, list_name_right[j]] = info_right[j].text
                except Exception as e:
                    print(f"[WARN] Lỗi thông tin chung tại {i}: {e}")

                # Hạn nộp
                try:
                    deadline = driver.find_elements(By.CLASS_NAME, "job-detail__information-detail--actions-label")
                    if deadline:
                        time_deadline = deadline[0].text.split(':')[1].strip()
                        df.loc[i, 'Hạn nộp'] = time_deadline
                except Exception as e:
                    print(f"[WARN] Lỗi hạn nộp tại {i}: {e}")

                time.sleep(random.uniform(3, 6))

            except Exception as e:
                print(f"[ERROR] Không thể truy cập {i}: {e}")

            finally:
                driver.quit()
                time.sleep(1)
    return df



