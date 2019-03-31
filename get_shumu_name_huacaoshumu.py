import requests
from lxml import etree


def get_shumu_name():
    headers = {

        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/72.0.3626.121 Mobile Safari/537.36'
    }

    basr_url = 'http://www.huacaoshumu.net/fenlei/shumu.php'
    response = requests.get(url=basr_url, headers=headers)
    text = etree.HTML(response.content)
    div_bao = text.xpath("//div[@class='bao']")
    i = 1
    name_list = []
    for div in div_bao:
        name = div.xpath("./a//text()")[0]
        # print(i, )
        name_list.append(name)
        i += 1
    print(name_list)


if __name__ == '__main__':
    get_shumu_name()