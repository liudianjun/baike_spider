import requests
from lxml import etree
import json
import re
import data_to_html
import time
import random
import os


class Baidu_obj(object):

    def __init__(self, plant_url, plant_name):
        self.base_url = plant_url
        self.headers = {}
        self.data_list = []
        self.plant = plant_name
        self.user_agetn = user_agent = [
        'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; '
        'Windows NT 5.1; (R1 1.5); .NET CLR 2.0.50727; InfoPath.1)',
        'Mozilla/5.0 (compatible; MSIE 9.0; AOL 9.7; AOLBuild 4343.19; Windows '
        'NT 6.1; WOW64; Trident/5.0; FunWebProducts)',
        'Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12'
    ]
        self.headers['User-Agent'] = random.choice(self.user_agetn)

    def response(self):
        print('正在请求{}数据'.format(self.plant))
        try:
            response_text = requests.get(self.base_url, headers=self.headers, verify=False)
            return response_text
        except:
            return None

    def parse_response(self):
        response = self.response()
        text = etree.HTML(response.content)
        try:
            main_content = text.xpath('//div[@class="main-content"]')
            # 如果没有数据 返回True

            # 获取基本信息
            subject_title = main_content[0].xpath(".//h1//text()")
            subject_summary = main_content[0].xpath(".//div[@class='lemma-summary']/div//text()")
            summary_pic = text.xpath(".//div[@class='side-content']//div[@class='summary-pic']//img/@src")
            print('summary_pic--->>', summary_pic)
            #获取基础信息
            base_info_name = main_content[0].xpath('./div[@class="basic-info cmn-clearfix"]//dt//text()')
            base_info_value = main_content[0].xpath('./div[@class="basic-info cmn-clearfix"]//dd//text()')
            result = [x.strip() for x in base_info_value if x.strip() != '']
            # print("base_info", len(base_info_name), base_info_name)
            # print("base_info", len(result), result)
            base_info_list = []
            for i in range(len(base_info_name)):
                base_info_dict = {
                    "name": base_info_name[i],
                    "value": result[i]
                }
                base_info_list.append(base_info_dict)
            # print("base_info_list", base_info_list)
            base_info = {
                'base_info': base_info_list
            }
            data_dict = {
                'subject_title': subject_title,
                'subject_summary': subject_summary,
                'summary_pic': summary_pic
            }
            self.data_list.append(data_dict)
            self.data_list.append(base_info)
            # 获取目录
            catalog_title = main_content[0].xpath('.//div[@class="para-title level-2"]//h2/text()')
            # 取第一个目录内容
            all_div = main_content[0].xpath('./div | ./table | ./ul')
            # table = main_content[0].xpath('./table')
            # if table[0] in all_div:
            #     print('==='*10)
            # print(table[0].xpath(".//text()"))
            # print(len(all_div), all_div)
            # print("all_div:", all_div)
            self.parse_catalog(catalog_title, all_div, self.plant)
        except Exception as e:
            return True

    # 根据一级目录遍历内容
    def parse_catalog(self, catalog_title, all_div, plant_name):
        # 遍历目录
        data_dict = {}
        for catalog in catalog_title:
            # print(catalog)
            # 寻找 2 级标题
            flag = 0
            for div in all_div:
                if len(div.xpath("./@class")) > 0:
                    # print(div.xpath("./@class")[0])
                    if div.xpath("./@class")[0] == 'para-title level-2':
                        # 判断二级标题的text（）是不是和当前遍历的目录一致
                        if div.xpath("./h2/text()")[0] == '':
                            pass
                        elif div.xpath("./h2/text()")[0] == catalog:
                            # print(div.xpath("./h2/text()")[0].strip())
                            self.parse_data(flag, catalog, data_dict, all_div)
                flag += 1
        # '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/json_file/东北山梅花.json'
        json_data = json.dumps(self.data_list, ensure_ascii=False)
        plant_json_name = '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/json_file/' + plant_name + '.json'
        with open(plant_json_name, 'w') as f:
            f.write(json_data)
        # print('--->', type(json_data), json_data)

    # 解析数据
    def parse_data(self, flag_data, catelog, data_dict, all_div):

        data_dict = {}
        src_data = ''
        data_dict["catalog_title"] = catelog
        for i in all_div[flag_data:]:
            # print('ul标签', i.tag)
            if len(i.xpath("./@log-set-param")) > 0:
                # print(i)
                self.parse_table(i)
                return
            if i.tag == 'ul':
                self.parse_ul_data(i)
                # print("ul标签：", i.attrib)
                # print("ul_text:", i.xpath(".//text()"))
                return
                # return
            if len(i.xpath("./@class")) > 0:
                if i.xpath("./@class")[0] == 'para':
                    # print("src_data---->", "".join(i.xpath(".//text()")).strip())
                    # 将文字信息拼接成字符串
                    src_data += "".join(i.xpath(".//text()")).strip()
                    src_data = re.sub('\[\d\]', '', src_data)
                    # 获取图片url

                    # catalog_url = i.xpath(".//a//img/@src | .//a/img/@src ")
                    # print('pic_url:', i.xpath(".//a//img//@src"))
                    if len(i.xpath(".//a//img/@src")) > 0:
                        if 'jpg' in i.xpath(".//a//img/@src")[0]:
                            # print('pic_url:', i.xpath(".//a//img/@src"))
                            catalog_url = i.xpath(".//a//img/@src")
                            # # print(catalog_url)
                            data_dict["catalog_url"] = catalog_url
                if i.xpath("./@class")[0] == 'para-title level-2':
                    if i.xpath("./h2/text()")[0] != catelog:
                        # print("src_data---->", src_data)
                        # src_data = re.sub('\[*\]', '', src_data)
                        data_dict['catalog_text'] = src_data.strip('\n')
                        self.data_list.append(data_dict)
                        return True
            flag_data += 1
        # print("src_data---->", src_data)
        data_dict['catalog_text'] = src_data.strip('\n')
        self.data_list.append(data_dict)

    # 解析列表，如果有
    def parse_table(self, i):

        data_dict = {}
        # print(i.xpath("./@log-set-param"))
        # 获取当前标签的上一个标签
        pre_div = i.xpath("./preceding-sibling::div[@class = 'para-title level-2'][1]")
        # print(pre_div[0].xpath(".//h2/text()"))
        data_dict["catalog_title"] = pre_div[0].xpath(".//h2/text()")[0]
        table_tr = i.xpath(".//tr")
        # print(len(table_tr), table_tr)
        # 遍历列表中的单个信息
        tr_list = []
        for tr in table_tr[1:]:
            tr_dict = {}
            # print('tr_tag:', tr.xpath("./th").tag)
            # tr.tag获取当前标签名
            # if 'th' in tr.xpath("./child::*")[0].tag:
            #     print('tr_tag:', tr.xpath("./th[3]//text()"))
            #     tr_name = tr.xpath("./th[2]//text()")
            #     tr_info = tr.xpath("./th[3]//text()")
            #     tr_dict['serial_num'] = ""
            #     tr_dict['name'] = tr_name
            #     tr_dict['info'] = tr_info
            #     continue

            tr_name = tr.xpath("./td[1]//text()")
            tr_info = "".join(tr.xpath("./td[2]//text()"))
            # 根据有没有图片链接判断是哪一种表
            # 改成 src属性
            print('pic_table:', tr.xpath("./td[3]//img/@src"))
            if tr.xpath("./td[3]//a/@src"):
                print('pic_table:', tr.xpath("./td[3]//a/@src"))
                tr_url = tr.xpath("./td[3]//a/@src")
                tr_dict['name'] = tr_name
                tr_dict['info'] = tr_info
                # tr_dict['url'] = tr_url
            else:
                tr_url = ''
                tr_dict['name'] = tr_name
                tr_dict['info'] = tr_info
                tr_dict['url'] = ''.join(tr.xpath("./td[3]//text()")).strip()

            # tr_dict['url'] = tr_url
            tr_list.append(tr_dict)
        data_dict['catalog_text'] = tr_list
        # print("---->>>", data_dict)
        self.data_list.append(data_dict)

    def parse_ul_data(self, data):

        data_dict = {}
        li_list = []
        # 获取当前标签的上一个标签
        pre_div = data.xpath("./preceding-sibling::div[@class = 'para-title level-2'][1]")
        # print(pre_div[0].xpath(".//h2/text()"))
        data_dict["catalog_title"] = pre_div[0].xpath(".//h2/text()")[0]

        li_lists = data.xpath("./li")
        for li in li_lists:
            # print("ul_info:")
            # print(li.xpath(".//text()"))
            li_data = ''.join(li.xpath(".//text()")).strip()
            li_list.append(li_data)
        # print(li_list)
        data_dict['catalog_text'] = li_list
        self.data_list.append(data_dict)


if __name__ == '__main__':
    new_name_list = ['柳树', '泡桐', '梧桐', '油桐', '国槐', '刺槐', '榆树', '桑树', '白杨', '松树', '苦楝', '香椿', '臭椿', '樟', '合欢树', '银杏', '三球悬铃木', '桂花',
                     '樱花', '发财树', '夹竹桃', '鸡爪槭', '凤凰木', '白兰', '玉兰', '广玉兰', '紫玉兰', '木棉', '丁香', '紫薇', '瑞香', '琼花', '紫荆', '梨树', '桃花', '李树',
                     '梅花', '杏花', '枣树', '阳桃', '枸杞', '芒果', '柠檬', '龙眼', '枫树', '构树', '榕树', '朴树', '梓树', '楸树', '橡树', '栾树', '白桦', '乌桕', '杜仲',
                     '珙桐', '棕榈', '杜英', '香榧', '冷杉', '紫檀', '云杉', '接骨木', '水东哥', '木奶果', '聚果榕', '大果榕', '嘉宝果', '鹅掌楸', '番石榴', '沙枣', '蟠桃', '槟榔',
                     '山竹', '蓝莓', '重阳木', '七叶树', '面包树', '菜豆树', '沙棘', '可可', '辣木', '皂荚', '花椒', '蛋黄果', '榛子', '栗子', '木犀榄', '马缨杜鹃', '葡萄',
                     '绣球荚蒾', '佛手', '榴莲', '山楂', '火棘', '金柑', '柚', '结香', '椰子', '雪松', '无患子', '无花果', '水杉', '十大功劳', '女贞', '南天竹', '木瓜', '龙爪槐',
                     '剑麻', '枫香树', '茶梅', '木槿', '香蕉', '杨梅', '淡竹', '紫叶李', '芭蕉', '石楠', '樱桃', '郁李', '榆叶梅', '西洋杜鹃', '皱皮木瓜', '四季海棠', '倒挂金钟',
                     '棣棠花', '胡杨', '猕猴桃', '木芙蓉', '枇杷', '山茶', '凤尾丝兰', '鹅掌柴', '咖啡树', '软叶刺葵', '杜鹃花', '桉树', '蜡梅', '青檀', '甜橙', '桃花心木', '白蜡',
                     '巴西木', '茶树', '绿玉树', '四合木', '石榴', '苏铁', '荔枝', '栗豆树', '橡皮树', '南烛', '南洋杉', '苹果', '蒲葵', '洋紫荆', '金鸡纳树', '金钱树', '卷柏',
                     '金樱子', '胡桃', '朱蕉', '棕竹', '夜香木兰', '海棠花', '黄栌', '红豆杉', '黑杨', '红背桂花', '常春藤', '海桐', '金银花', '锦带花', '连翘', '美人蕉', '柿子',
                     '迎春花', '玉簪花', '月季', '栀子']
    # plant_name_list = ['旱柳', '绦柳', '馒头柳', '垂柳', '金丝垂柳', '加拿大杨', '银中杨', '新疆杨', '榆树', '垂榆', '欧洲白榆', '小叶朴', '刺槐', '国槐', '山皂角', '稠李', '山桃', '红花山桃', '白花山桃', '山杏', '元宝槭', '复叶械', '绒毛白蜡', '美国花曲柳', '梓树', '圆柏', '沈阳桧', '暴马丁香', '臭椿', '油松', '红松', '华山松', '白皮松', '圆柏', '沈阳桧', '西安桧', '丹东桧', '塔桧', '东北红豆杉', '矮紫杉', '朝鲜黄杨', '照白杜鹃', '红皮云杉', '青杆云杉', '白杆云杉', '杉松冷杉', '沙地柏', '铺地柏', '兴安桧', '玉兰', '日本厚朴', '天女木兰', '山楂', '山里红', '山荆子', '红肉苹果', '稠李', '山桃', '红花山桃', '白花山桃', '山杏', '山桃稠李', '东北杏', '辽梅杏', '山梨', '东北连翘', '连翘', '迎红杜鹃', '榆叶梅', '重瓣榆叶梅', '鸾枝', '毛樱桃', '珍珠花', '白千瓣麦李', '红千瓣麦李', '三裂绣线菊', '土庄绣线菊', '紫丁香', '欧丁香', '白丁香', '四季丁香', '早花锦带', '花楸', '山槐', '香花槐', '栾树', '刺槐', '暴马丁香', '梓树', '美国梓树', '黄金树', '辽东丁香', '什锦丁香', '锦带花', '红王子锦带', '东北山梅花', '京山梅花', '小花溲疏', '香茶蔟', '水枸子', '齿叶白鹃梅', '重瓣棣棠', '风箱果', '多季玫瑰', '冷香玫瑰', '黄刺玫', '白玉棠', '珍珠梅', '猬实', '日本绣线菊', '毛果绣线菊', '柳叶绣线菊', '树锦鸡儿', '大花铁线莲', '忍冬', '台尔曼忍冬', '金银忍冬', '桃色忍冬', '金露梅', '水蜡', '胡枝子', '大花圆锥绣球', '日本绣线菊', '金露梅', '东陵八仙花', '花木兰', '桃叶卫矛', '荆条', '金叶莸', '中宁枸杞', '秦岭忍冬', '接骨木', '花蓼', '紫叶矮樱', '紫叶稠李', '紫叶小檗', '金山绣线菊', '金焰绣线菊', '金叶莸', '银杏', '白桦', '小叶朴', '元宝械', '珍珠花', '黄檗', '火炬树', '假色械', '拧筋械', '茶条械', '毛脉卫矛', '胶东卫矛', '红瑞木', '迎红杜鹃', '照白杜鹃', '五叶地锦', '地锦', '软枣猕猴桃', '南蛇藤', '山葡萄', '大花铁线莲', '花蓼', '五叶地锦', '地锦', '台尔曼忍冬', '忍冬', '沙地柏', '铺地柏', '兴安桧', '五叶地锦', '地锦', '忍冬', '金山绣线菊', '日本绣线菊', '金焰绣线菊', '珍珠花', '水蜡', '金叶莸', '紫叶小檗']
    plant_name_list = ['白桦树']
    # plant_name_list = ['暴马丁香', '臭椿', '油松', '红松', '华山松', '白皮松', '圆柏', '沈阳桧', '西安桧', '丹东桧', '塔桧', '东北红豆杉', '矮紫杉', '朝鲜黄杨', '照白杜鹃', '红皮云杉', '青杆云杉', '白杆云杉', '杉松冷杉', '沙地柏', '铺地柏', '兴安桧', '玉兰', '日本厚朴', '天女木兰', '山楂', '山里红', '山荆子', '红肉苹果', '稠李', '山桃', '红花山桃', '白花山桃', '山杏', '山桃稠李', '东北杏', '辽梅杏', '山梨', '东北连翘', '连翘', '迎红杜鹃', '榆叶梅', '重瓣榆叶梅', '鸾枝', '毛樱桃', '珍珠花', '白千瓣麦李', '红千瓣麦李', '三裂绣线菊', '土庄绣线菊', '紫丁香', '欧丁香', '白丁香', '四季丁香', '早花锦带', '花楸', '山槐', '香花槐', '栾树', '刺槐', '暴马丁香', '梓树', '美国梓树', '黄金树', '辽东丁香', '什锦丁香', '锦带花', '红王子锦带', '东北山梅花', '京山梅花', '小花溲疏', '香茶蔟', '水枸子', '齿叶白鹃梅', '重瓣棣棠', '风箱果', '多季玫瑰', '冷香玫瑰', '黄刺玫', '白玉棠', '珍珠梅', '猬实', '日本绣线菊', '毛果绣线菊', '柳叶绣线菊', '树锦鸡儿', '大花铁线莲', '忍冬', '台尔曼忍冬', '金银忍冬', '桃色忍冬', '金露梅', '水蜡', '胡枝子', '大花圆锥绣球', '日本绣线菊', '金露梅', '东陵八仙花', '花木兰', '桃叶卫矛', '荆条', '金叶莸', '中宁枸杞', '秦岭忍冬', '接骨木', '花蓼', '紫叶矮樱', '紫叶稠李', '紫叶小檗', '金山绣线菊', '金焰绣线菊', '金叶莸', '银杏', '白桦', '小叶朴', '元宝械', '珍珠花', '黄檗', '火炬树', '假色械', '拧筋械', '茶条械', '毛脉卫矛', '胶东卫矛', '红瑞木', '迎红杜鹃', '照白杜鹃', '五叶地锦', '地锦', '软枣猕猴桃', '南蛇藤', '山葡萄', '大花铁线莲', '花蓼', '五叶地锦', '地锦', '台尔曼忍冬', '忍冬', '沙地柏', '铺地柏', '兴安桧', '五叶地锦', '地锦', '忍冬', '金山绣线菊', '日本绣线菊', '金焰绣线菊', '珍珠花', '水蜡', '金叶莸', '紫叶小檗']
    for plant in plant_name_list:
        if plant in new_name_list:
            print('因存在这条数据')
            continue
        elif os.path.exists('/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/json_file/{}.json'.format(plant)):
            print('JSON文件已存在')
            continue
        else:
            url = 'https://baike.baidu.com/search/word?word={}'.format(plant)
            no_data = Baidu_obj(plant_url=url, plant_name=plant).parse_response()
            if no_data:
                continue
            time.sleep(5)
            if os.path.exists('/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/Mobile-AutoBookmark/{}.html'.format(plant)):
                print('HTML文件已存在')
            is_file_err = data_to_html.main_to_html(plant)
            print(is_file_err)
            time.sleep(1)

