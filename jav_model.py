"""
Crawler info of JAV models and insert into database via SQlite
"""
import re
import sqlite3

from requests_html import HTMLSession

BASE_URL = 'https://javmodel.com'
s = HTMLSession()
conn = sqlite3.connect('porn.db')
c = conn.cursor()


def crawl_urls():
    urls = []
    for page in range(1, 42):
        print(f'Page {page}')
        r = s.get(f'https://javmodel.com/jav/homepages.php?page={page}')
        hrefs = r.html.xpath('//div[@class="portfolio columns-4"]/div//a[@class="mask"]/@href')
        urls += map(lambda x: BASE_URL + x, hrefs)
    with open('urls.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
    return urls


def clean_data(data, datatype):
    if data:
        r_data = data.group()
    elif datatype is int:
        r_data = 0
    else:
        r_data = ''
    return r_data


def crawl_model(url):
    r = s.get(url)
    info_element = r.html.xpath('//div[contains(@class, "col-sm-9")]')[0]
    personal_info, video_info = info_element.xpath('//ul')
    born_date, blood, breast, waist, hips, height = personal_info.xpath('//li/text()')
    model_style, video_classes, video_count = video_info.xpath('//li')

    model_name = info_element.xpath('//h2/text()')[0]
    born_date = re.search(r'\d+/\d+/\d+', born_date)
    blood = re.search(r'\w+$', blood)
    breast = re.search(r'\d+', breast)
    hips = re.search(r'\d+', hips)
    waist = re.search(r'\d+', waist)
    height = re.search(r'\d+', height)
    model_style = model_style.xpath('//a/text()')
    video_classes = video_classes.xpath('//a/text()')
    video_count = re.search(r'\d+', video_count.text)

    born_date = clean_data(born_date, int)
    blood = clean_data(blood, str)
    breast = clean_data(breast, int)
    hips = clean_data(hips, int)
    waist = clean_data(waist, int)
    height = clean_data(height, int)
    model_style = ', '.join(model_style)
    video_classes = ', '.join(video_classes)
    video_count = clean_data(video_count, int)

    data = (model_name, born_date, blood, breast, hips, waist,
            height, model_style, video_classes, video_count)

    c.execute('''INSERT INTO jav(model_name, born_date, blood, breast, hips, waist,
                                 height, model_style, video_classes, video_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)


def main():
    with open('urls.txt') as f:
        urls = f.read().splitlines()
    for i, url in enumerate(urls, start=1):
        print(i)
        crawl_model(url)


if __name__ == '__main__':
    main()
    conn.commit()
    conn.close()
