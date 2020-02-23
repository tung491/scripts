"""
Create card in Trello which consists the lessons of course in Coursera
"""
import os
import sys
import time

import requests
from requests_html import HTML
from selenium import webdriver

TRELLO_KEY = os.getenv('trello_key')
TRELLO_TOKEN = os.getenv('trello_token')

driver = webdriver.Chrome('/Users/tung491/Downloads/chromedriver')


def login():
    username = os.getenv('cousera_username')
    password = os.getenv('cousera_password')
    driver.implicitly_wait(10)
    driver.get('https://www.coursera.org/?authMode=login')
    driver.find_element_by_name('email').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    time.sleep(45)


def crawler(link):
    driver.get(link)
    base_url = 'https://www.coursera.org'
    r = HTML(html=driver.page_source)
    course_name_xpath = '//div[@class="rc-Welcome"]/div/div//h1/text()'
    course_name = r.xpath(course_name_xpath)[0]
    weeks_hrefs = r.xpath('//*[@id="rendered-content"]/div/div/div/div[2]/nav/div[1]/div/a/@href')
    weeks_hrefs = [base_url + url for url in weeks_hrefs]
    table_of_content = {}
    for week_href in weeks_hrefs:
        driver.get(week_href)
        time.sleep(7)
        r = HTML(html=driver.page_source)
        heading_elements = r.xpath('//div[@class="rc-NamedItemList"]')
        for heading_element in heading_elements:
            heading_text = heading_element.xpath('//h3/text()')[0]
            elements = heading_element.xpath('//div[@class="rc-WeekItemName headline-1-text"]/text()')
            table_of_content[heading_text] = elements
    return course_name, table_of_content


def create_card(list_id, course_name):
    url = "https://api.trello.com/1/cards"
    querystring = {"key": TRELLO_KEY, "token": TRELLO_TOKEN, 'idList': list_id, 'name': course_name}
    result = ''
    try:
        response = requests.request("post", url, params=querystring).json()
        result = response['id']
    except KeyError:
        pass
    print(result)
    return result


def create_checklist(card_id, table_of_content):
    checkitem_url = "https://api.trello.com/1/checklists/{}/checkItems"
    checklist_url = "https://api.trello.com/1/checklists"
    headings = table_of_content.keys()

    for heading in headings:
        querystring = {"idCard": card_id, "key": TRELLO_KEY, "token": TRELLO_TOKEN, 'name': heading}
        checklist_id = ''
        try:
            response = requests.request("POST", checklist_url, params=querystring).json()
            checklist_id = response['id']
            print(checklist_id)
        except KeyError:
            pass
        check_items = table_of_content[heading]
        for check_item in check_items:
            querystring = {'name': check_item, 'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
            respone = requests.request("POST", checkitem_url.format(checklist_id), params=querystring)
            try:
                print(respone.json()['id'])
            except KeyError:
                pass


def main():
    links = sys.argv[1:]
    login()
    for link in links:
        course_name, table_of_content = crawler(link)
        time.sleep(5)
        card_id = create_card('5def99afb68c414582951a66', course_name)
        create_checklist(card_id, table_of_content)

    print('Done')


if __name__ == '__main__':
    main()
