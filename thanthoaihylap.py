"""
Crawl images of Than thoai Hy Lap and generate comic ebooks from those
"""
import os
import time

import requests
from requests_html import HTMLSession


def main():
    s = HTMLSession()
    link_fmt = 'https://truyenqq.com/truyen-tranh/than-thoai-hy-lap-2637-chap-{}.html'
    links = [link_fmt.format(i) for i in range(1, 73)]
    count = 1
    try:
        os.mkdir('Thần thoại Hy Lạp')
    except:
        pass
    os.chdir('Thần thoại Hy Lạp').
    os.mkdir('Quyển 1')
    os.chdir('Quyển 1')
    for i, link in enumerate(links, start=1):
        r = s.get(link)
        img_urls = r.html.xpath('//div[@class="story-see-content"]//img/@src')
        print('Chap {}'.format(i))
        for img_url in img_urls:
            img_content = requests.get(img_url).content
            with open(f'{count}.jpg'.zfill(5), 'wb') as f:
                f.write(img_content)
            count += 1
        if i % 7 == 0:
            os.chdir('..')
            os.mkdir('Quyển {}'.format((i // 7) + 1))
            os.chdir('Quyển {}'.format((i // 7) + 1))
        time.sleep(1)


if __name__ == '__main__':
    main()
