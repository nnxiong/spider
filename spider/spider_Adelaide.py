import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import random
import pandas as pd
from urllib.parse import urljoin


def get_links(base_url: str, search_info: str, headers: str):
    """
    获取研究人员详细信息链接
    return: 研究人员详细信息链接
    """
    # scan_all = False
    professor_links = []
    postdoc_links = []
    page = 0
    # get the last page all page
    ## 获取源码
    all_page = 0
    school = search_info.rsplit("page=")[0]
    school_url = f"{base_url}{school}"
    try:
        html = requests.get(school_url, headers=headers)
        html.encoding = 'utf-8' # 防止乱码
        soup = BeautifulSoup(html.text, "html.parser")
        page_li = soup.find("ul", class_="c-pagination").find_all("li")
        name_link = page_li[-1].find('a')
        if name_link:
            href = name_link['href']
        else:
            href = page_li[-3].find('a')['href']
        all_page = int(href.rsplit("=", 1)[-1]) + 1
    except Exception as e:
        # 捕获所有异常，并打印异常信息
        print(f"An error occurred: {e}")

    for page in tqdm(range(all_page), desc="Crawling staff links"):
        info_url = f"{base_url}{search_info}{page}"
        try:
            ## 获取源码
            html = requests.get(info_url, headers=headers)
            html.encoding = 'utf-8' # 防止乱码
            soup = BeautifulSoup(html.text, "html.parser")

            # 解析源码
            # 查找目标div
            target_div = soup.find('div', class_='c-media-object__row is-stacked has-four-columns js-equalize')
            if target_div:
                # 定位 section
                sections = target_div.find_all('section', class_='c-media-object__column')
                for section in sections:
                    # 获取h2中的a标签（姓名链接）
                    name_link = section.find('h2').find('a')
                    href = name_link['href'] if name_link else None
                    
                    # 检查i标签（职称）或a标签文本中是否包含关键词
                    title_tag = section.find('i')
                    title_text = title_tag.get_text(strip=True) if title_tag else ""

                    # 确保有链接
                    if href:
                        if ("Professor" in title_text and "Associate" not in title_text) or ("Professor" in name_link.get_text(strip=True) and "Associate" not in name_link.get_text(strip=True)):
                            professor_links.append(href)
                        elif "Postdoctoral Researcher" in title_text or "Postdoctoral Researcher" in name_link.get_text(strip=True):
                            postdoc_links.append(href)
            page += 1
            sleep_time = random.uniform(0.4, 0.6)
            time.sleep(sleep_time)
        except Exception as e:
            # 捕获所有异常，并打印异常信息
            print(f"An error occurred: {e}")
    
    # 合并所有链接并去重
    all_links = list(set(professor_links + postdoc_links))
    # 转换为完整URL
    full_links = [urljoin(base_url, link) for link in all_links]
    
    return full_links


def get_researcher_details(profile_links: str, headers: str):
    """
    获取研究人员详细信息（带进度条版本）
    :param profile_urls: 研究人员个人主页URL列表
    :return: 包含所有研究人员信息的列表
    """
    all_researchers = []
    for link in tqdm(profile_links, desc="Crawling staff details", unit="profile"):
        try:
            # 发送HTTP请求获取页面内容
            html = requests.get(link, headers=headers)
            html.encoding = 'utf-8' # 防止乱码
            soup = BeautifulSoup(html.text, 'html.parser')
            
            # 提取基本信息
            name = soup.find('h1', class_='docs-heading').get_text(strip=True)
            
            position = soup.find('p', class_='position').get_text(strip=True) if soup.find('p', class_='position') else ""
            department = soup.find('p', class_='department').get_text(strip=True) if soup.find('p', class_='department') else ""
            organisation = soup.find('p', class_='organisation').get_text(strip=True) if soup.find('p', class_='organisation') else ""
            
            # 提取个人简介
            bio_paragraphs = []
            bio_div = soup.find('div', class_='bio')
            if bio_div:
                field_item = bio_div.find('div', class_='field-item')
                if field_item:
                    bio_paragraphs = [p.get_text(strip=True) for p in field_item.find_all('p')]
            # 提取 Email
            email = ""
            email_tag = soup.find('div', class_='c-tabs__container')        
            bio_div = email_tag.find('ul', class_='c-icon-detail-list')
            li_tags = bio_div.find_all('li')
            for li in li_tags:
                li_strong = li.find('strong')
                if li_strong and li_strong.get_text(strip=True) == 'Email:':
                    email = li.find('a').get_text(strip=True)
                    break

            # 构建结果字典
            researcher_data = {
                'name': name,
                'position': position,
                'department': department,
                'organisation': organisation,
                'email': email,
                'biography': '\n'.join(bio_paragraphs),  # 将多个段落合并为一个字符串
                'link': link
            }
            all_researchers.append(researcher_data)
        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
            return None
    return all_researchers    



def save_to_excel(data: str, filename: str):
    """
    将数据保存到Excel文件
    """
    df = pd.DataFrame(data)
    # 确保列顺序正确
    df = df[['name', 'position', 'department', 'organisation', 'email', 'biography', 'link']]
    df.to_excel(filename, index=False)
    print(f"数据已保存到 {filename}")


if __name__ == '__main__':
    begin = time.time() 
    base_url = "https://researchers.adelaide.edu.au/"
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "Referer": "https://researchers.adelaide.edu.au/"
    }

    # 1 医学院：Adelaide Medical School (2694)
    # search_info = "?name=&keywords=&department=Adelaide%20Medical%20School%20%282694%29&page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/Adelaide_Medical_School.xlsx"
    # 2 生物医学学院: School of Biomedicine (4428)
    # search_info = "?name=&keywords=&department=School+of+Biomedicine+%284428%29page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/School_of_Biomedicine.xlsx"
    # 3 生物科学学院: School of Biological Sciences (69)
    search_info = "?name=&keywords=&department=School+of+Biological+Sciences+%2869%29page="
    data_save_file = "/mnt/data1/zhongrongmiao/spider/info/School_of_Biological_Sciences.xlsx"
    # search_info_school = [search_info1, search_info2, search_info3]
    # step 1
    # full_links = get_links(base_url, search_info_school, headers)
    full_links = get_links(base_url, search_info, headers)
    # step 2
    researcher_data = get_researcher_details(full_links, headers)
    # save details
    if researcher_data:
        save_to_excel(researcher_data, data_save_file)
    times = time.time() - begin
    print(f"爬取时间：{times}")


