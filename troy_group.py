import csv
import os
import time

import requests
from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TELEGRAM_BASE_URL = f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/'

WINDOW_SIZE = "1920,1080"
CHROMEDRIVER_PATH = '/Users/tung491/Downloads/chromedriver'
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                          options=chrome_options)


def login():
    driver.get('https://www.facebook.com/groups/899962870068722/')
    driver.find_element_by_name('email').send_keys(os.getenv('fb_username'))
    driver.find_element_by_name('pass').send_keys(os.getenv('fb_pass'))
    driver.find_element_by_id('u_0_2').click()
    time.sleep(10)
    page_source = driver.page_source
    return page_source


def get_attached_file(post):
    attached_file = ''
    for link in post.links:
        if link.startswith('https://www.facebook.com/download/'):
            attached_file = link
            break
    return attached_file


def cleanup_text(text):
    lines = text.splitlines()
    if lines[-1] == 'See Translation':
        lines.remove(lines[-1])
    cleaned_text = '\n'.join(lines)
    return cleaned_text


def parser(page_source):
    r = HTML(html=page_source)
    data = []
    posts = r.xpath('//div[contains(@class, "userContent")]')
    for post in posts:
        try:
            content = post.xpath('//div[contains(@data-testid, "post_message")]')[0]
        except IndexError:
            continue
        text = content.text
        text = cleanup_text(text)
        attached_file = get_attached_file(post)
        data.append((text, attached_file))
    return data


def read_prv_posts():
    with open('troy_posts.csv') as f:
        reader = csv.reader(f)
        lines = list(line[0] for line in reader)
    return lines


def send_message(msg):
    url = TELEGRAM_BASE_URL + 'sendMessage'
    params = {'chat_id': '470727343',
              'text': msg}
    r = requests.post(url, params=params)
    if not r.ok:
        print(r.content)


def main():
    page_source = login()
    data = parser(page_source)
    prv_posts = read_prv_posts()
    with open('troy_posts.csv', 'a') as f:
        writer = csv.writer(f)
        for post in set(data):
            if post[0] in prv_posts:
                continue
            send_message('\n'.join(post))
            print('\n'.join(post))
            writer.writerow(post)

    driver.close()


if __name__ == '__main__':
    main()
