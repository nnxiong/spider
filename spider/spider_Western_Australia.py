from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import random
import pandas as pd
# from selenium import webdriver
import cloudscraper #


def get_researcher_details(base_url: str, school: str, headers: str):
    """
    获取研究人员详细信息链接
    return: 研究人员详细信息链接
    """
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 无界面模式
    # driver = webdriver.Chrome(options=options)
    scraper = cloudscraper.create_scraper()
    page = 0
    # get the last page all page
    all_page = 1
    url = f"{base_url}{school}{page}"
    try:
        # html = requests.get(url, headers=headers)
        html = scraper.get(url, headers=headers)
        html.encoding = 'utf-8' # 防止乱码
        soup = BeautifulSoup(html.text, "html.parser")
        # 解析源码
        # extract department
        department = soup.find('div', class_="organisation-details").find("h1").get_text(strip=True)
        # extract pages
        page_nav = soup.find("nav", class_="pages").find_all("li")
        name_link = page_nav[-2].find('a')
        if name_link:
            all_page = int(name_link.get_text(strip=True))
    except Exception as e:
        # 捕获所有异常，并打印异常信息
        print(f"An error occurred: {e}")
    all_researchers = []
    researchers_info = []
    for page in tqdm(range(all_page), desc="Crawling staff links"):
        # info_url = f"{base_url}{search_info}{page}"
        info_url = f"{base_url}{school}{page}"
        try:
            ## 获取源码
            html = scraper.get(info_url, headers=headers)
            html.encoding = 'utf-8' # 防止乱码
            soup = BeautifulSoup(html.text, "html.parser")
            # 查找目标div
            target_div = soup.find('ul', class_='grid-results')
            if target_div:
                # 定位 target_li
                target_li = [child for child in target_div.children if child.name == 'li']
                # target_li = target_div.find_all('li')
                for section in target_li:
                    # Extract position
                    tar_ul = section.find('ul', class_="relations organisations")
                    title_element = tar_ul.find_all('span', class_='minor dimmed')
                    position = ""
                    if title_element:
                        for tile in title_element:
                            text = tile.get_text(strip=True)
                            if ("Professor" in text and "Associate" not in text and "Assistant" not in text) or "Postdoctoral Research" in text:
                                position = text
                                break
                    if not position:
                        continue
                    
                    # Extract email
                    email_element = section.find('a', class_='email')
                    if not email_element:
                        continue
                    email = "".join([info for info in email_element.children if info.name != "script"]).strip()
                    # Extract name
                    target_h3 = section.find("h3")
                    name = target_h3.find('span').get_text(strip=True)
                    # Extract profile link
                    profile_link = target_h3.find("a")['href']
                    
                    researcher_data = {
                        'name': name,
                        'position': position,
                        'department': department,
                        'email': email,
                        'link': profile_link
                    }
                    researchers_info.append(researcher_data)

            page += 1
            sleep_time = random.uniform(0.8, 1)
            time.sleep(sleep_time)
        except Exception as e:
            # 捕获所有异常，并打印异常信息
            print(f"An error occurred: {e}")
    
    for researcher in tqdm(researchers_info, desc="Crawling staff details"):
        link = researcher['link']
        try:
            html = scraper.get(link, headers=headers)
            html.encoding = 'utf-8' # 防止乱码
            soup = BeautifulSoup(html.text, "html.parser")
            # 查找包含教授详细信息的<p>标签
            target_half = soup.find("div", class_="half")
            bio = target_half.find("h3").get_text(strip=True)
            if bio == "Biography":
                target_p = target_half.find("div", class_="textblock").find_all('p')
                bio1 = target_p[0].get_text(strip=True)
                bio2 = ""
                if 1 < len(target_p):
                    bio2 = target_p[1].get_text(strip=True)
            researcher['biography'] = ' '.join([bio1, bio2])  # 合并多余空格
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
    base_url = "https://research-repository.uwa.edu.au/en/organisations/"
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "cookie":'_gcl_au=1.1.710621204.1747015698; userType=prospective student; _tt_enable_cookie=1; _ttp=01JV1402253THHC99EDD7WF6W8_.tt.2; bid_uwaxn1f61qtsuguu5wqmobzgtgj7ew7f=4e70c774-d800-47ec-9ae8-3d8b1186e686; _scid=rgx-Qk0WpclXVL1jmfjci7cROsAclPIr; _fbp=fb.2.1747015699558.229697155214079465; _ga=GA1.1.97182980.1747015700; ELOQUA=GUID=AAF4B94AEC4B4D0A8B005EA10C256BBA; FPID=FPID2.3.6wx%2Fae9J9u8jbtMLINoEOxrJtZNTIoCObqRgQAb6Nwg%3D.1747015700; _gtmeec=e30%3D; _ScCbts=%5B%5D; _sctr=1%7C1746979200000; FPAU=1.3.710621204.1747015698; OptanonAlertBoxClosed=2025-05-13T08:07:22.269Z; _ga=GA1.4.97182980.1747015700; _gid=GA1.4.1532676778.1747123643; _gcl_au=1.4.710621204.1747015698; JSESSIONID=EAB72A74F09FD72D94C6526B57C287D9.DS9ApacTomcatC1; AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg=1; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-2121179033%7CMCIDTS%7C20222%7CMCMID%7C07254581758524112340364657466464993852%7CMCAAMLH-1747789606%7C6%7CMCAAMB-1747789606%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1747192006s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.3.0; FPLC=JpqgrI4f4wfgzlWRJ%2BdfXpyU15447BzvYrrnlVQyaIa%2B%2BlZZCa8wo41aFOwmoKZ105lk4XMcVZFKcpNLlZ8Bzg52L42vnORcxpQXpEOakTAFRRSGqoOECZ%2B6xIeKTw%3D%3D; _clck=1g1ijsd%7C2%7Cfvw%7C0%7C1958; bx_bucket_number=111; bx_guest_ref=ecae393e-26c7-43a4-9eff-d32c354e1417; __cf_bm=Cw.VHhZh5.2df5q5l1GS4fUuSUdpZ1cpdUOapGm9n5Q-1747186903-1.0.1.1-gE3fi7YSd.6.jI6OjbLqrTv8rvjQhM.Rfpebx_vZL_ZYLB4cYxYxRTcKD0KFlOSbfjjoATd0DjtjAF60YAovIHfAEIwhlCYi0v3UfGPh_tE; _ga_886292W0J6=GS2.1.s1747187184$o9$g0$t1747187184$j60$l0$h0; _ga_3TZVGFFX6H=GS2.1.s1747187185$o9$g0$t1747187185$j60$l0$h0; _ga_2YDLQ05G5S=GS2.1.s1747187185$o9$g0$t1747187185$j0$l0$h0; _ga_1234567890=GS2.1.s1747187185$o9$g0$t1747187185$j0$l0$h568301262; _ga_FQKYCDD16S=GS2.1.s1747187185$o9$g0$t1747187185$j0$l0$h0; _scid_r=sYx-Qk0WpclXVL1jmfjci7cROsAclPIrVODp4g; ttcsid=1747187188280::Fr1XyFznhKPhNxMApqnD.9.1747187188280; ttcsid_CJVASLRC77U5TJETTUFG=1747187188278::DxbJPzJwuOIlGFYpEETJ.8.1747187188880; _clsk=icmmlp%7C1747187342445%7C2%7C1%7Ce.clarity.ms%2Fcollect; OptanonConsent=isGpcEnabled=0&datestamp=Wed+May+14+2025+09%3A51%3A02+GMT%2B0800+(GMT%2B08%3A00)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=71845a82-c387-4e7f-8dd0-818426372643&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C4%3A1&intType=1&geolocation=HK%3B&AwaitingReconsent=false; _ga_886292W0J6=GS2.4.s1747187184$o9$g1$t1747187462$j34$l0$h0; _ga_BBYVK7X433=GS2.4.s1747184803$o3$g1$t1747187462$j34$l0$h0; s_pers=%20v8%3D1747187462325%7C1841795462325%3B%20v8_s%3DLess%2520than%25201%2520day%7C1747189262325%3B%20c19%3Dpr%253Apure%2520portal%253Aorganisations%253Arelations%7C1747189262327%3B%20v68%3D1747186376768%7C1747189262330%3B; s_sess=%20s_cpc%3D0%3B%20c13%3Dname-asc%3B%20c7%3Dtype%253D%252Fdk%252Fatira%252Fpure%252Forganisation%252Forganisationtypes%252Forganisation%252Fs%3B%20e41%3D1%3B%20s_cc%3Dtrue%3B%20s_ppvl%3Dpr%25253Apure%252520portal%25253Apersons%25253Aview%252C25%252C25%252C924%252C1912%252C924%252C1920%252C1080%252C1%252CP%3B%20s_ppv%3Dpr%25253Apure%252520portal%25253Aorganisations%25253Arelations%252C35%252C29%252C1124%252C932%252C924%252C1920%252C1080%252C1%252CP%3B',
        "Referer": "https://research-repository.uwa.edu.au/"
    }
    # 医学
    # search_info ="school-of-allied-health/persons/?page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/uwa/school_of_allied_health.xlsx"
    search_info ="uwa-medical-school/persons/?page="
    data_save_file = "/mnt/data1/zhongrongmiao/spider/info/uwa/uwa_medical_school.xlsx"
    # # 生物
    # search_info ="school-of-biological-sciences/persons/?page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/uwa/school_of_biological_sciences.xlsx"
    # search_info ="school-of-biomedical-sciences/persons/?page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/uwa/school_of_biomedical_sciences.xlsx"
    # # # 环境
    # search_info ="uwa-school-of-agriculture-and-environment/persons/?page="
    # data_save_file = "/mnt/data1/zhongrongmiao/spider/info/uwa/school_of_agriculture_and_environment.xlsx"
    # search_info_school = [search_info1, search_info2, search_info3]
    # step 1
    researcher_data = get_researcher_details(base_url, search_info, headers)
    # save details
    if researcher_data:
        save_to_excel(researcher_data, data_save_file)
    times = time.time() - begin
    print(f"爬取时间：{times}")


