from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import base64
import json
from openpyxl import Workbook

# 创建Excel工作簿并设置表头
wb = Workbook()
ws = wb.active
ws.title = "深圳房源数据"
ws.append(["页码", "房源序号", "房东", "价格"])  # 添加表头

# 配置浏览器选项禁止加载图片
chrome_options = Options()
prefs = {
    "profile.managed_default_content_settings.images": 2  # 禁用图片
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # 进一步禁用图片

driver = webdriver.Chrome(options=chrome_options)  # 传入配置


for page in range(1, 8):
    print(f"正在爬取第{page}页")
    items_offset = (page - 1) * 18
    section_offset = 0
    version = 1
    dic_cursor = {
        "section_offset":0,
        "items_offset":items_offset,
        "version":1
    }
    cursor = base64.b64encode(json.dumps(dic_cursor).encode("utf-8")).decode("utf-8")
    base_url = "https://zh.airbnb.com/s/%E4%B8%AD%E5%9B%BD%E5%B9%BF%E4%B8%9C%E7%9C%81%E6%B7%B1%E5%9C%B3%E5%B8%82/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2025-02-01&monthly_length=3&monthly_end_date=2025-05-01&price_filter_input_type=0&channel=EXPLORE&query=%E4%B8%AD%E5%9B%BD%E5%B9%BF%E4%B8%9C%E7%9C%81%E6%B7%B1%E5%9C%B3%E5%B8%82&place_id=ChIJkVLh0Aj0AzQRyYCStw1V7v0&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=5&ne_lat=22.721988369786303&ne_lng=114.22871502485799&sw_lat=22.348799239016813&sw_lng=113.91952863697054&zoom=10.70616856904252&zoom_level=10&search_by_map=true&pagination_search=true"
    federated_search_session_id = "f5e11e48-9f05-49f2-b5db-4baab8b78577"

    # 用 & 把base_url federated_search_session_id 和 cursor 连接起来
    url = f"{base_url}&federated_search_session_id={federated_search_session_id}&cursor={cursor}"

    #构造完每页的url后，我们就可以开始正式爬取信息了
    driver.get(url)
    driver.maximize_window()
    # 强制滚动加载完整列表
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 显式等待页面元素加载
    wait = WebDriverWait(driver, 20)
    rent_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g1qv1ctd")))

    # 遍历房源并保存数据
    for index, eachhouse in enumerate(rent_list):
        try:
            price_element = WebDriverWait(eachhouse, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span._11jcbg2"))
            )
            price = price_element.text

            host_element = WebDriverWait(eachhouse, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.a8jt5op"))
            )
            host = host_element.text

            # 将数据写入Excel
            ws.append([page, index + 1, host, price])
            print(f"第{page}页：房源 {index + 1} | 房东：{host} | 价格：{price} ")

        except Exception as e:
            # 写入错误信息占位符
            ws.append([page, index + 1, "获取失败", "获取失败"])
            print(f"房源 {index + 1} 信息获取失败:", str(e))

    print(f"第{page}页爬取完毕，暂停2秒，准备爬取{page + 1}页\n")
    sleep(2)


print("爬取完毕，保存数据并关闭浏览器")
driver.quit()
wb.save("D:\Desktop\深圳airbnb房源数据.xlsx")  # 保存Excel文件
print("数据已保存到D盘桌面“深圳airbnb房源数据.xlsx”")








