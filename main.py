import random
import time
import requests
import re
from lxml import etree
from pandas import DataFrame
from fake_useragent import UserAgent

class Postgrad:
    def __init__(self, search_data):
        """初始化函数，设置用户代理、请求URL和查询参数。

        Args:
            search_data (dict): 查询时需要的参数。
        """
        self.user_agent = UserAgent()  # 使用fake_useragent库生成随机的用户代理
        self.url = "https://yz.chsi.com.cn/zsml/queryAction.do" 
        # 初始数据表头
        self.data = [["所在地", "招生单位", "考试方式", "院系所", "专业", "学习方式", "研究方向", "指导老师", "拟招人数", "备注", "考试范围"]]
        self.search_data = search_data  # 查询参数
    
    def _request(self, url, method='get', data=None):
        """发送网络请求。

        Args:
            url (str): 请求的URL地址。
            method (str, optional): 请求方法('get'或'post')。默认为'get'。
            data (dict, optional): POST请求的数据。默认为None。

        Returns:
            str: 请求返回的HTML内容，如果请求失败则返回None。
        """
        headers = {'User-Agent': self.user_agent.random}  # 设置请求头，包括随机的User-Agent
        try:
            if method == 'post':
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查响应状态，如果不是200则引发异常
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def _parse_html(self, text):
        """解析HTML内容。

        Args:
            text (str): HTML文本。

        Returns:
            _Element: 解析后的HTML根元素。
        """
        return etree.HTML(text)
    
    def _get_max_page(self, html):
        """获取查询结果的最大页数。

        Args:
            html (_Element): HTML的根元素。

        Returns:
            int: 最大页数。
        """
        page_text = html.xpath('//ul[@class="ch-page"]/li[last()-2]/a/text()')
        return int(page_text[0]) if page_text else 1
    
    def _get_school_urls(self, html):
        """从HTML中提取学校页面的URLs。

        Args:
            html (_Element): HTML的根元素。

        Returns:
            list[tuple]: 包含(url, location)的列表。
        """
        base_url = "https://yz.chsi.com.cn"
        return [(base_url + path, location) for path, location in 
                zip(html.xpath('//table[@class="ch-table"]/tbody//a/@href'),
                    html.xpath('//table[@class="ch-table"]/tbody//tr//td[2]//text()'))]
    
    def _get_college_urls(self, html):
        """从HTML中提取具体学院的URLs。

        Args:
            html (str): HTML文本。

        Returns:
            list[str]: 学院URL的列表。
        """
        base_url = "https://yz.chsi.com.cn"
        paths = re.findall('<a href="(.*?)" target="_blank">查看</a>', html)
        return [base_url + path for path in paths]
    
    def _extract_data(self, html):
        """从HTML中提取需要的数据。

        Args:
            html (_Element): HTML的根元素。

        Returns:
            list[str]: 提取出的数据列表。
        """
        results = html.xpath('//td[@class="zsml-summary"]//text()')
        remarks = ''.join(html.xpath('//span[@class="zsml-bz"]//text()'))
        items = ''.join(html.xpath('//tbody[@class="zsml-res-items"]//td/text()'))
        return results + [remarks, items]
    
    def fetch_data(self):
        """主函数，用于抓取数据并填充到self.data中。"""
        first_page_html = self._request(self.url, 'post', self.search_data)
        if not first_page_html:
            return
        
        html = self._parse_html(first_page_html)
        max_pages = self._get_max_page(html)
        
        for page in range(1, max_pages + 1):
            print("正在抓取页面:", page)
            self.search_data['pageno'] = page
            page_html = self._request(self.url, 'post', self.search_data)
            if not page_html:
                continue
            
            page_html_parsed = self._parse_html(page_html)
            school_urls = self._get_school_urls(page_html_parsed)
            for url, location in school_urls:
                college_html = self._request(url)
                if not college_html:
                    continue
                
                college_html_parsed = self._parse_html(college_html)
                college_urls = self._get_college_urls(college_html)
                for college_url in college_urls:
                    print("处理中:", college_url)
                    final_html = self._request(college_url)
                    if not final_html:
                        continue
                    
                    final_html_parsed = self._parse_html(final_html)
                    data = [location] + self._extract_data(final_html_parsed)
                    self.data.append(data)
                    time.sleep(random.uniform(2, 5))
    
    def save_data(self):
        """保存数据到CSV文件。"""
        df = DataFrame(self.data[1:], columns=self.data[0])
        df.to_csv("result.csv", index=False, encoding="utf_8_sig")

if __name__ == '__main__':
    search_data = {
        "ssdm": "",  # 输入省市代码
        "dwmc": "",  # 输入高校名称
        "mldm": "07",  # 学科门类代码
        "mlmc": "",
        "yjxkdm": "0711",  # 输入学科类别代码（必填项，其他项需选择一项填入）
        "zymc": "",  # 这里输入专业名称
        "xxfs": "",  # 这里输入学习方式
        "pageno": ""  # 查询的指定页数
    }
    spider = Postgrad(search_data)
    spider.fetch_data()
    spider.save_data()
    print("数据抓取和保存完成。")
