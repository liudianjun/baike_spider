import json


def read_json(json_file_path):
    # 读取json文件
    with open(json_file_path, 'r') as load_f:
        json_data = json.load(load_f)
        # print(data)

    # print(subject_title, subject_summary)
    return json_data


def read_html(template_file_data):
    # 读取html文件
    with open(template_file_data, 'r') as f:
        template_data = f.read()

    return template_data


def writer(json_data, template_file_data, plant):
    # print(json_data, type(template_file_data))
    # 简介内容
    try:
        subject_title = json_data[0]['subject_title'][0]
        subject_summary = ''.join(json_data[0]['subject_summary'])
        summary_pic = None
        if len(json_data[0]['summary_pic']) > 0:
            summary_pic = json_data[0]['summary_pic'][0]
        # 基础信息
        base_info = json_data[1]['base_info']
        # print(base_info)
        new_html_data = template_file_data.replace('{subject_title_field}', subject_title)
        # 插入url
        if summary_pic:
            new_html_data = new_html_data.replace('{subject_img_field}', summary_pic)
        # else:
        #     subject_summary_url = subject_summary
        new_html_data = new_html_data.replace('{subject_summary_field}', subject_summary)
        # 插入基础信息
        str_info = []
        if len(base_info) > 0:
            for info in base_info:
                key = info['name']
                value = info['value']
                str_info.append('<li> <span>{}：</span>{} </li>'.format(key, value))
        new_html_data = new_html_data.replace('{base_info_filed}', ''.join(str_info))
        # 遍历其他信息
        catalog = []

        flag = 3
        for data in json_data[2:]:
            # print(data)
            catalog_title = data['catalog_title']
            catalog_texts = data['catalog_text']
            # print(data.keys())
            # 如果有图片链接
            if 'catalog_url' in data.keys():
                catalog_url = ''.join(data['catalog_url'])
                # print(data['catalog_url'])
                catalog.append('''
                            <section id="catelog_{}">
                                    <h2 class="f20 pl16 pr16 ">{}</h2>
                                    <div class="item-content f14 lh160 v-pd2-p">
                                    <p class="tc reset"><a class="pic show-tip" style="width: 288px; height: 186px;">
                                <img class="js-haveLarge" alt="白桦" title="白桦" data-index="2" src="{}" style="opacity: 1;"></a></p>
    
                                        <p>
                                            {}
                                        </p>
    
                                    </div>
                                </section>
                            '''.format(flag, catalog_title, catalog_url, catalog_texts))
                flag += 1
            # print('计数', len(catalog_texts), type(catalog_texts))
            # 如果数据是个列表 则里面有多个数据
            elif isinstance(catalog_texts, list):

                # print('catalog_texts:', data)
                catalog_text_list = []
                i = 1
                for catalog_text in catalog_texts:
                    if isinstance(catalog_text, dict):
                        print('这是字典', catalog_text)
                        catalog_text_list.append('''
                                        <li> <span>{}：</span>{} {}</li>
                                        '''.format(catalog_text['name'], catalog_text['info'], catalog_text['url']))
                        i += 1
                    else:
                        catalog_text_list.append('''
                        <li> <span>{}：</span>{} </li>
                        '''.format(i, catalog_text))
                        i += 1
                catalog.append('''
                <section id="catelog_{}">
                        <h2 class="f20 pl16 pr16 ">{}</h2>
                        <div class="item-content f14 lh160 v-pd2-p">
                            <p>
                                {}
                            </p>
                            
                        </div>
                    </section>
                '''.format(flag, catalog_title, ''.join(catalog_text_list)))
            # print(data)
                flag += 1
            # 其他情况

            else:
                catalog.append('''
                                    <section id="catelog_{}">
                                            <h2 class="f20 pl16 pr16 ">{}</h2>
                                            <div class="item-content f14 lh160 v-pd2-p">
                                                <p>
                                                    {}
                                                </p>
    
                                            </div>
                                        </section>
                                    '''.format(flag, catalog_title, catalog_texts))
                # print(data)
                flag += 1
        new_html_data = new_html_data.replace('{catalog}', ''.join(catalog))

        output_new_html(new_html_data, plant)
        return 1
    except Exception as e:
        return 0



def output_new_html(new_html_data, plant):

    file_name = '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/Mobile-AutoBookmark/{}.html'.format(plant)
    with open(file_name, 'w') as f:
        f.write(new_html_data)


def main_to_html(plant):
    json_file_path = '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/json_file/' +plant + '.json'
    json_file_path = json_file_path
    template_file_path = '/Users/liudianjun/Desktop/WorkSpace/爬虫/百度百科项目/Mobile-AutoBookmark/template-auto-bookmark.html'
    json_data = read_json(json_file_path)
    template_file_data = read_html(template_file_path)
    print('正在写入{}数据'.format(plant))
    is_file_err = writer(json_data, template_file_data, plant)
    if is_file_err:
        return '写入HTML完毕'
    else:
        return '数据错误'


if __name__ == '__main__':
    main_to_html()