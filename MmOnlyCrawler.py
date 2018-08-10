import time
import os
import requests
from lxml import html

def get_image_dir():
    return './Photos/mm'

def get_main_page():
    return 'http://www.mmonly.cc/wmtp/wmxz/'

def get_page_selector(url):
    r = requests.get(url)
    r.encoding = 'gb2312'
    response = r.text
    return html.fromstring(response)

#获得栏目总页数
def get_page_count():
    selector = get_page_selector(get_main_page())
    lastAddr = selector.xpath("//div[@id='pageNum']/a[last()]/@href")[0]
    arr = lastAddr.split('_')
    length = len(lastAddr)-len(arr[-1])
    pageBase = lastAddr[0:length]
    pageCount = arr[-1].split('.')[0]
    return pageCount, pageBase  #返回有多少页，并且返回页地址前缀 (页地址前缀+页号+.html)

#获得栏目所有页地址
def get_pages_addr():
    pageCount, pageBase = get_page_count()
    pages = []
    for i in range(1, int(pageCount)+1):
        pages.append(get_main_page() + pageBase + str(i) + '.html')
    return pages

#获得某一页所有套图地址
def get_atlas_addr_by_page(url):
    selector = get_page_selector(url)
    atlases = selector.xpath("//div[@class='ABox']/a/@href")
    return atlases

#获得套图的标题和图数
def get_image_title(atlas):
    selector = get_page_selector(atlas)
    image_title = selector.xpath("//div[@class='wrapper clearfix imgtitle']/h1/text()")[0]
    count_text = selector.xpath("//div[@class='pages']/ul/li/a/text()")[0]
    #去掉共字和页字
    count = count_text[1:len(count_text)-3]
    return image_title, count

#下载套图
def download_image(atlas):
    title, count = get_image_title(atlas)

    #创建文件夹
    dir = os.path.join(get_image_dir(), title)
    os.makedirs(dir, 0o777, True)
    #创建套图页面列表
    imagehtmladdrs = [atlas]
    for i in range(2,int(count)+1):
        imagehtmladdrs.append(atlas[0:len(atlas)-5] + '_' + str(i) + atlas[len(atlas)-5:])
    num = 1
    #下载套图所有图片
    for imagehtmladdr in imagehtmladdrs:
        selector = get_page_selector(imagehtmladdr)
        try:
            imageaddr = selector.xpath("//div[@id='big-pic']/p/a/img/@src")[0]
        except:
            imageaddr = selector.xpath("//div[@id='big-pic']/p/img/@src")[0]
        filename = '%s.jpg' % (num)
        filepath = os.path.join(dir,filename)
        if not os.path.exists(filepath):
            print('正在下载图片：%s第%s/%s张，' % (title, num, count))
            with open(filepath, 'wb') as f:
                f.write(requests.get(imageaddr).content)
        else:
            print('跳过下载图片：%s第%s/%s张，' % (title, num, count))
        num += 1
        #time.sleep(1);

if __name__ == '__main__':
    #page_number = input('请输入需要爬取的页码：')
    pagenum = 1
    for page in get_pages_addr():
        if pagenum < 0:
            pagenum += 24
            continue
        atlases = get_atlas_addr_by_page(page)
        for atlas in atlases:
            retry = 10
            while True:
                try:
                    retry -= 1
                    download_image(atlas)
                    break
                except:
                    if(retry < 0):
                        break
                    else:
                        continue
        pagenum += 1
