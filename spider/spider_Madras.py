import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import pandas as pd
from urllib.parse import urljoin
import re

def get_info(base_url, department_label, headers):
    all_researchers = []
    researchers_info = []
    department_url = f"{base_url}{department_label}"
    try:
        html = requests.get(department_url, headers=headers, verify=False)
        html.encoding = 'utf-8' # 防止乱码
        soup = BeautifulSoup(html.text, "html.parser")
        # find department
        department = soup.find('div', class_='esc-heading').find('h3').text.strip()
        # Find all faculty entries
        faculty_entries = soup.find_all('div', class_='row faculty-border')

        for faculty in tqdm(faculty_entries, desc="Crawling staff info"):
            # Extract title/position
            position = faculty.find('h5', class_='post').text.strip()
            if "Professor" in position and "Associate" not in position and "Assistant" not in position:
                # Extract name
                name = faculty.find('h3', class_='name').text.strip()
                # Extract email
                envelope_icon = faculty.find('i', class_='fa fa-envelope')
                email = envelope_icon.next_sibling.strip()
                # Extract profile link
                profile_link = faculty.find('a', string='Read Profile')['href']
                researcher_data = {
                    'name': name,
                    'position': position,
                    'department': department,
                    'email': email,
                    'link': profile_link
                }
                researchers_info.append(researcher_data)
    except Exception as e:
        # 捕获所有异常，并打印异常信息
        print(f"An error occurred: {e}")

    for researcher in tqdm(researchers_info, desc="Crawling staff details"):
        link = researcher['link']
        try:
            html = requests.get(link, headers=headers, verify=False)
            html.encoding = 'utf-8' # 防止乱码
            soup = BeautifulSoup(html.text, "html.parser")
            # 查找包含教授详细信息的<p>标签
            professor_info0 = soup.find('div', class_='faculty-detail no-border').find('p')
            professor_info1 = professor_info0.get_text(strip=True)
            professor_info_more = professor_info0.find('span', id="more").get_text(strip=True)
            # 提取文本并清理空白
            researcher['biography'] = '\n'.join([professor_info1, professor_info_more])  # 合并多余空格
            all_researchers.append(researcher)
        except Exception as e:
            # 捕获所有异常，并打印异常信息
            print(f"An error occurred: {e}")
    
    return all_researchers

def save_to_excel(data: str, filename: str):
    """
    将数据保存到Excel文件
    """
    df = pd.DataFrame(data)
    # 确保列顺序正确
    df = df[['name', 'position', 'department', 'email', 'biography', 'link']]
    df.to_excel(filename, index=False)
    print(f"数据已保存到 {filename}")


if __name__ == '__main__':
    begin = time.time() 
    base_url = "https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid="
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
    }
    """
    - 医学：
        - Department of Anatomy 生物化学系：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=3
        - Department of Endocrinology 内分泌学系：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=29
        - Department of Genetics 遗传学系：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=33
        - Department of Medical Biochemistry 医学生物化学系：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=49
    - 生物：
        - Department of Biotechnology：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=11
        - Department of Biochemistry：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=10
    - 环境：
        - Centre for Environmental Sciences 环境科学中心：https://www.unom.ac.in/index.php?route=department/department/deptpage&deptid=86
    """
    department_label_0 = "3"
    data_save_file_0 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Anatomy.xlsx"
    department_label_1 = "29"
    data_save_file_1= "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Endocrinology.xlsx"
    department_label_2 = "33"
    data_save_file_2 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Genetics.xlsx"
    department_label_3 = "49"
    data_save_file_3 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Medical_Biochemistry.xlsx"
    department_label_4 = "11"
    data_save_file_4 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Biotechnology.xlsx"
    department_label_5 = "10"
    data_save_file_5 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Biochemistry.xlsx"
    department_label_6 = "86"
    data_save_file_6 = "/mnt/data1/zhongrongmiao/spider/info/Madras_Department_of_Centre_for_Environmental Sciences.xlsx"

    department_label_list = [department_label_0, department_label_1, department_label_2, department_label_3, department_label_4, department_label_5, department_label_6]
    data_save_file_list = [data_save_file_0, data_save_file_1, data_save_file_2, data_save_file_3, data_save_file_4, data_save_file_5, data_save_file_6]
    for department_label, file in zip(department_label_list, data_save_file_list):
        researcher_data = get_info(base_url, department_label, headers)
        # save details
        if researcher_data:
            save_to_excel(researcher_data, file)
    times = time.time() - begin
    print(f"爬取时间：{times}")


