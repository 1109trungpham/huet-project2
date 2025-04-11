from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import re
import random

def page_total():
    driver = webdriver.Chrome()
    driver.get("https://www.topcv.vn/tim-viec-lam-ai-engineer?")
    time.sleep(2)

    try:
        text = driver.find_element(By.ID, "job-listing-paginate-text").text
        # text ví dụ: "1 / 4 trang"
        match = re.search(r'/\s*(\d+)\s*trang', text)
        if match:
            total_pages = int(match.group(1))
        else:
            print("Không tìm thấy số trang.")
            return None
    except Exception as e:
        print("Lỗi:", e)
        return None
    driver.quit()
    time.sleep(1)
    return total_pages

title_ls = []
company_ls = []
job_link_ls = []
company_link_ls = []

def crawl1(page_number):
    url = f'https://www.topcv.vn/tim-viec-lam-ai-engineer?type_keyword=1&page={page_number}'
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)
    bodys = driver.find_elements(By.CLASS_NAME, "body") # Lấy tất cả các ô chứa bài viết tuyển dụng

    for body in bodys:
        try:
            title = body.find_element(By.CSS_SELECTOR, "h3.title > a > span").text    # Lấy tiêu đề
        except:
            title = "N/A"
        try:
            company = body.find_element(By.CLASS_NAME, "company-name").text    # Lấy tên công ty
        except:
            company = "N/A"
        try:
            job_link = body.find_element(By.CSS_SELECTOR, "h3.title > a").get_attribute("href")    # Lấy link công việc
        except:
            job_link = "N/A"
        try:
            company_link = body.find_element(By.CSS_SELECTOR, "a.company").get_attribute("href")    # Lấy link công ty
        except:
            company_link = "N/A"

        title_ls.append(title)
        company_ls.append(company)
        job_link_ls.append(job_link)
        company_link_ls.append(company_link)

        time.sleep(1)
    driver.quit()
    time.sleep(1)
    return None

def crawl2(df: pd.DataFrame):
    for jobl in df['Job_link']:
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
                print(f"[WARN] Lỗi job info tại {jobl}: {e}")
                salary = location = experience = "N/A"

            df.loc[jobl, 'Location'] = location
            df.loc[jobl, 'Experience'] = experience
            df.loc[jobl, 'Salary'] = salary

            # Chi tiết tuyển dụng
            try:
                names_left = driver.find_elements(By.CLASS_NAME, "job-description__item")
                list_name_left = [name.get_attribute("textContent").strip().split('\n')[0] for name in names_left]
                info_left = driver.find_elements(By.CLASS_NAME, "job-description__item--content")

                for i in range(min(len(list_name_left), len(info_left))):
                    if list_name_left[i] == "Cách thức ứng tuyển":
                        break
                    df.loc[jobl, list_name_left[i]] = info_left[i].text
            except Exception as e:
                print(f"[WARN] Lỗi chi tiết tuyển dụng tại {jobl}: {e}")

            # Thông tin chung
            try:
                name_right = driver.find_elements(By.CLASS_NAME, "box-general-group-info-title")
                list_name_right = [name.text for name in name_right]
                info_right = driver.find_elements(By.CLASS_NAME, "box-general-group-info-value")

                for i in range(min(len(list_name_right), len(info_right))):
                    df.loc[jobl, list_name_right[i]] = info_right[i].text
            except Exception as e:
                print(f"[WARN] Lỗi thông tin chung tại {jobl}: {e}")

            # Hạn nộp
            try:
                deadline = driver.find_elements(By.CLASS_NAME, "job-detail__information-detail--actions-label")
                if deadline:
                    time_deadline = deadline[0].text.split(':')[1].strip()
                    df.loc[jobl, 'Hạn nộp'] = time_deadline
            except Exception as e:
                print(f"[WARN] Lỗi hạn nộp tại {jobl}: {e}")

            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"[ERROR] Không thể truy cập {jobl}: {e}")

        finally:
            driver.quit()
            time.sleep(1)

    # Xử lý dataframe
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={
        "Job_link": "Link công việc",
        "Company_link": "Link công ty",
        "Company": "Tên công ty",
        "Title": "Tiêu đề",
        "Location": "Khu vực",
        "Experience": "Kinh nghiệm",
        "Salary": "Thu nhập"
    }, inplace=True)
    df.drop_duplicates(inplace=True)
    return df


def main():
    for page_num in range(1, page_total()+1):
        crawl1(page_num)

    df = pd.DataFrame({"Title" : title_ls,
                       "Company" : company_ls,
                       "Job_link" : job_link_ls,
                       "Company_link" : company_link_ls
                       })
    
    df.set_index(keys='Job_link', drop=False, inplace=True)
    data = crawl2(df)
    data.to_csv('~/Desktop/topcv.csv', index=False)

if __name__=='__main__':
    main()


# Nếu thiếu dữ liệu do bị chặn bởi trình xác thực người dùng, hãy chạy lại hàm dưới đây cho đến khi nhận được đầy đủ dữ liệu
from crawl_again import crawl_again

path_to_data ='~/Desktop/topcv.csv'
# data = crawl_again(path_to_data)
# data.to_csv('~/Desktop/topcv_full.csv', index=False)
