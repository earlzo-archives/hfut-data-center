# -*- coding:utf-8 -*-
"""
高德Web服务API向开发者提供http接口，开发者可通过http请求获取各类型的地理数据服务

http://lbs.amap.com/api/webservice/summary/
"""
from __future__ import unicode_literals, print_function, division
import json
import hashlib
import logging

from six import string_types, text_type, iteritems, python_2_unicode_compatible
from six.moves import urllib

ERRORS = {
    '10000': '请求正常',
    '10001': 'key不正确或过期',
    '10002': '没有权限使用相应的服务或者请求接口的路径拼写错误',
    '10003': '访问已超出日访问量',
    '10004': '单位时间内访问过于频繁',
    '10005': 'IP白名单出错，发送请求的服务器IP不再IP白名单内',
    '10006': '绑定域名无效',
    '10007': '数字签名未通过验证',
    '10008': 'MD5安全码未通过验证',
    '10009': '请求key与绑定平台不符',
    '10010': 'IP访问超限',
    '10011': '服务不支持https请求',
    '20000': '请求参数非法',
    '20001': '缺少必填参数',
    '20002': '请求协议非法',
    '20003': '其他未知错误',
    '20800': '规划点（包括起点、终点、途经点）不在中国陆地范围内',
    '20801': '划点（起点、终点、途经点）附近搜不到路',
    '20802': '路线计算失败，通常是由于道路连通关系导致'
}


def handle_error(result_dict):
    if result_dict['status'] == '1':
        result_dict.pop('status')
        result_dict.pop('infocode')
        result_dict.pop('info')
        return result_dict
    info_code = result_dict['infocode']
    error_msg = 'API request error! [{:s}]{:s} {:s}'
    raise ValueError(error_msg.format(info_code, result_dict['info'], ERRORS[info_code]))


@python_2_unicode_compatible
class Location(object):
    def __init__(self, *args, lon=None, lat=None):
        l = len(args)
        try:
            if l == 0:
                assert lon and lat
                self.lon = lon
                self.lat = lat
            else:
                assert not (lon or lat)
                if l == 1:
                    assert isinstance(args[0], string_types)
                    self.lon, self.lat = map(lambda v: float(v), args[0].split(','))
                elif l == 2:
                    self.lon, self.lat = map(lambda v: float(v), args)
                else:
                    raise AssertionError
        except AssertionError:
            raise ValueError('错误的初始化参数')

    def __str__(self):
        return ','.join([text_type(self.lon), text_type(self.lat)])

    def __iter__(self):
        for v in (self.lon, self.lat):
            yield v


class AMap(object):
    host = 'http://restapi.amap.com/v3/'

    def __init__(self, key, secret_key=None):
        self.key = key
        self.secret_key = secret_key

    def request(self, url, **api_kwargs):
        url = urllib.parse.urljoin(self.host, url)
        parameters = {}
        for k, v in iteritems(api_kwargs):
            if not v:
                continue
            if not isinstance(v, string_types):
                if hasattr(v, '__iter__'):
                    v = '|'.join(map(lambda s: text_type(s), v))
                if isinstance(v, bool):
                    v = text_type(v).lower()
            parameters[k] = v
        parameters.setdefault('key', self.key)
        parameters.setdefault('output', 'json')
        query = sorted(parameters.items())
        query_str = urllib.parse.urlencode(query, doseq=True)
        if self.secret_key is not None:
            sig = hashlib.md5(''.join([urllib.parse.unquote_plus(query_str),
                                       self.secret_key]).encode()).hexdigest()
            query_str = ''.join([query_str, '&sig=', sig])
        url = '?'.join([url, query_str])
        logging.debug('API request url: %s', url)
        response = urllib.request.urlopen(url)
        response_text = response.read().decode()
        result = json.loads(response_text)
        logging.debug('API response: %s', result)
        return handle_error(result)

    # 地理/逆地理编码API http://lbs.amap.com/api/webservice/reference/georegeo/

    def geo(self, address, city=None):
        """
        地理编码

        :param address: 结构化地址信息, 规则： 省+市+区+街道+门牌号
        :param city: 查询城市, 可选值：城市中文、中文全拼、citycode、adcode, 如：北京/beijing/010/110000
        """
        url = 'geocode/geo'
        return self.request(url, address=address, city=city)

    def regeo(self, location, poitype=1000, radius=1000, extensions='base', batch=False, roadlevel=None, homeorcorp=0):
        """
        逆地理编码

        :param location: 经纬度坐标, 规则： 最多支持20个坐标点。多个点之间用"|"分割。经度在前，纬度在后，经纬度间以“，”分割，经纬度小数点后不得超过6位
        :param poitype: 返回附近POI类型, 支持传入POI TYPECODE及名称；支持传入多个POI类型，多值间用“|”分隔，extensions=all时生效，不支持batch=true(逆地理编码批量查询)
        :param radius: 搜索半径, 取值范围：0~3000,单位：米
        :param extensions: 返回结果控制, 此项默认返回基本地址信息；取值为all返回地址信息、附近POI、道路以及道路交叉口信息。
        :param batch: 批量查询控制, batch=true为批量查询。batch=false为单点查询，batch=false时即使传入多个点也只返回第一个点结果
        :param roadlevel: 道路等级, 可选值：1，当roadlevel=1时，过滤非主干道路，仅输出主干道路数据
        :param homeorcorp: 是否优化POI返回顺序,

        可选参数:0,1,2, 默认:0
        - 0：不优化。
        - 1：综合大数据将居家相关的主POI结果优先返回，即优化pois字段之中的poi顺序。
        - 2：综合大数据将公司相关的主POI结果优先返回，即优化pois字段之中的poi顺序。
        """
        url = 'geocode/regeo'
        return self.request(url, location=location, poitype=poitype, radius=radius, extensions=extensions, batch=batch,
                            roadlevel=roadlevel, homeorcorp=homeorcorp)

    # 输入提示API http://lbs.amap.com/api/webservice/reference/inputtips/

    def input_tips(self, keywords, type=None, location=None, city=None, citylimit=False, datatype='all'):
        """
        输入提示API

        - 产品介绍

            输入提示是一类简单的HTTP接口，提供根据用户输入的关键词查询返回建议列表。

            该套API免费对外开放，使用API您需先申请key，若无高德地图API账号需要先申请账号，企业用户单个key支持20万次/天，1万次/分钟。

        - 适用场景
            配合搜索服务-ID查询API使用（Place API）：先通过输入提示服务API接口，可获取根据关键字查询返回的建议列表，用户选择列表中的一项，通过POI ID完成ID搜索服务，获取POI详细信息。

        - 使用限制

            - 企业用户：单个key支持20万次/天，1万次/分钟调用。
            - 普通用户：单个key支持1000次/天调用

        :param keywords: 查询关键词
        :param type: POI分类, 服务可支持传入多个分类，多个类型剑用“|”分隔, 可选值：POI分类名称、分类代码
        :param location: 坐标, 经度,纬度, 建议使用location参数，可在此location附近优先返回搜索关键词信息
        :param city: 搜索城市, 可选值：城市中文、中文全拼、citycode、adcode, 如：北京/beijing/010/110000
        :param citylimit: 仅返回指定城市数据, 可选值：true/false
        :param datatype: 返回的数据类型, 多种数据类型用“|”分隔，可选值：all-返回所有数据类型、poi-返回POI数据类型、bus-返回公交站点数据类型、busline-返回公交线路数据类型
        """
        url = 'assistant/inputtips'
        return self.request(url, keywords=keywords, type=type, location=location, city=city, citylimit=citylimit,
                            datatype=datatype)

    # 搜索API http://lbs.amap.com/api/webservice/reference/search/

    def search_by_keywords(self, keywords=None, types=None, city=None, citylimit=False, children=None, offset=20,
                           page=1, extensions='base'):
        """
        关键字搜索

        keywords和types两者至少必选其一

        :param keywords: 查询关键字, 规则： 多个关键字用“|”分割
        :param types: 查询POI类型, 多个类型用“|”分割；
可选值：文本分类、分类代码（建议使用分类代码，避免文本分类输入错误操作的搜索失败）
分类代码由六位数字组成，后四位为0代表大类名称，后两位为0代表小类名称，如需搜索大类下所有分类，输入去掉后尾0。
例如：180000为道路附属服务， 全类别下搜索types=18;搜索下一分类警示信息，types=1801; 搜索再下级分类，types=180101
        :param city: 查询城市, 可选值：城市中文、中文全拼、citycode、adcode
如：北京/beijing/010/110000
        :param citylimit: 仅返回指定城市数据
可选值：true/false
        :param children: 是否按照层级展示子POI数据, 可选值：children=1
        :param offset: 每页记录数据, 最大每页记录数为50条。超出取值范围按最大值返回
        :param page: 当前页数, 最大翻页数100
        :param extensions: 	返回结果控制, 此项默认返回基本地址信息；取值为all返回地址信息、附近POI、道路以及道路交叉口信息。
        """
        url = 'place/text'
        return

    def search_by_around(self, location, keywords=None, types=None, city=None, radius=3000, sortrule='distance',
                         offset=20, page=1, extensions='base'):
        """
        周边搜索

        :param location: 中心点坐标, 规则： 经度和纬度用","分割，经度在前，纬度在后，经纬度小数点后不得超过6位
        :param keywords: 查询关键字, 规则： 多个关键字用“|”分割
        :param types: 查询POI类型, 多个类型用“|”分割；
可选值：文本分类、分类代码（建议使用分类代码，避免文本分类输入错误操作的搜索失败）
分类代码由六位数字组成，后四位为0代表大类名称，后两位为0代表小类名称，如需搜索大类下所有分类，输入去掉后尾0。
例如：180000为道路附属服务， 全类别下搜索types=18;搜索下一分类警示信息，types=1801; 搜索再下级分类，types=180101
        :param city: 查询城市, 可选值：城市中文、中文全拼、citycode、adcode
如：北京/beijing/010/110000
        :param radius: 查询半径, 取值范围:0-50000。规则：大于50000按默认值，单位：米
        :param sortrule: 排序规则, 按距离排序：distance；综合排序：weight
        :param offset: 每页记录数据, 最大每页记录数为50条。超出取值范围按最大值返回
        :param page: 当前页数, 最大翻页数100
        :param extensions: 返回结果控制, 此项默认返回基本地址信息；取值为all返回地址信息、附近POI、道路以及道路交叉口信息。
        :return:
        """
        url = 'place/around'
        return

    def search_by_polygon(self, polygon, keywords=None, types=None, offset=20, page=1, extensions='base'):
        """
        多边形搜索

        :param polygon: 经纬度坐标对, 规则：经度和纬度用","分割，经度在前，纬度在后，坐标对用";"分割。经纬度小数点后不得超过6位。 多边形为矩形时，可传入左上右下两顶点坐标对；其他情况下首尾坐标对需相同。
        :param keywords: 查询关键字, 规则： 多个关键字用“|”分割
        :param types: 查询POI类型, 多个类型用“|”分割；
可选值：文本分类、分类代码（建议使用分类代码，避免文本分类输入错误操作的搜索失败）
分类代码由六位数字组成，后四位为0代表大类名称，后两位为0代表小类名称，如需搜索大类下所有分类，输入去掉后尾0。
例如：180000为道路附属服务， 全类别下搜索types=18;搜索下一分类警示信息，types=1801; 搜索再下级分类，types=180101
        :param offset: 每页记录数据, 最大每页记录数为50条。超出取值范围按最大值返回
        :param page: 当前页数, 最大翻页数100
        :param extensions: 返回结果控制, 此项默认返回基本地址信息；取值为all返回地址信息、附近POI、道路以及道路交叉口信息。
        :return:
        """
        url = 'place/polygon'
        return

    def search_by_id(self, id):
        """
        ID查询

        :param id: 兴趣点id, 兴趣点的唯一标识ID, 如: B0FFFZ7A7D
        """
        url = 'place/detail'
        return

    # 路径规划API http://lbs.amap.com/api/webservice/reference/direction/

    def walking_direction(self, origin, destination):
        """
        步行路径规划

        :param origin: 出发点, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        :param destination: 目的地, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        """
        url = 'direction/walking'
        return

    def bus_direction(self, origin, destination, city, cityd=None, extensions='base', strategy=0, nightflag=0,
                      date=None, time=None):
        """
        公交路径规划

        :param origin: 出发点, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        :param destination: 目的地, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        :param city: 城市/跨城规划时的起点城市
目前支持市内公交换乘/跨城公交的起点城市。
可选值：城市名称/citycode
        :param cityd: 跨城公交规划时的终点城市
跨城公交规划必填参数。
可选值：城市名称/citycode
        :param extensions: 返回结果详略
可选值：base(default)/all
base:返回基本信息；all：返回全部信息
        :param strategy: 公交换乘策略
可选值：
0：最快捷模式
1：最经济模式
2：最少换乘模式
3：最少步行模式
5：不乘地铁模式
        :param nightflag: 是否计算夜班车
可选值：0：不计算夜班车
1：计算夜班车
        :param date: 出发日期
根据出发时间和日期筛选可乘坐的公交路线，格式：date=2014-3-19
        :param time: 出发时间
根据出发时间和日期筛选可乘坐的公交路线，格式：time=22:34
        """
        url = 'direction/transit/integrated'
        return

    def driving_direction(self, origin, destination, originid=None, destinationid=None, strategy=0, waypoints=None,
                          avoidpolygons=None, avoidroad=None):
        """
        驾车路径规划

        :param origin: 出发点, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        :param destination: 目的地, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        :param originid: 出发点poiid, 当起点为POI时，建议填充此值。
        :param destinationid: 目的地poiid, 当终点为POI时，建议填充此值。
        :param strategy: 驾车选择策略

0速度优先（时间）

1费用优先（不走收费路段的最快道路）

2距离优先

3不走快速路

4躲避拥堵

5多策略（同时使用速度优先、费用优先、距离优先三个策略计算路径）

6不走高速

7不走高速且避免收费

8躲避收费和拥堵

9不走高速且躲避收费和拥堵
        :param waypoints: 途经点

经度和纬度用","分割，经度在前，纬度在后，小数点后不超过6位，坐标点之间用";"分隔

最大数目：16个坐标点
        :param avoidpolygons: 避让区域

区域避让，支持32个避让区域，每个区域最多可有16个顶点

经度和纬度用","分割，经度在前，纬度在后，小数点后不超过6位，坐标点之间用";"分隔，区域之间用"|"分隔。如果是四边形则有四个坐标点，如果是五边形则有五个坐标点；

同时传入避让区域及避让道路，仅支持避让道路
        :param avoidroad: 避让道路名

只支持一条避让道路
        """
        url = 'direction/driving'
        return

    def distance(self, origins, destination):
        """
        行驶距离测量

        :param origins: 出发点, 支持100个坐标对，坐标对见用“| ”分隔；经度和纬度用","分隔
        :param destination: 目的地, 规则： lon,lat（经度,纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位
        """
        url = 'distance'
        return

    def static_map(self, location, zoom, size='400*400', scale=1, markers=None, labels=None, paths=None, traffic=0):
        """
        静态地图服务通过返回一张地图图片响应HTTP请求，使用户能够将高德地图以图片形式嵌入自己的网页中。用户可以指定请求的地图位置、图片大小、以及在地图上添加覆盖物，如标签、标注、折线、多边形。

        :param location: 地图中心点	中心点坐标。 规则：经度和纬度用","分隔 经纬度小数点后不得超过6位。
        :param zoom: 地图级别	地图缩放级别:[1,17]
        :param size: 地图大小	图片宽度*图片高度。最大值为1024*1024
        :param scale: 普通/高清	1:返回普通图； 2:调用高清图，图片高度和宽度都增加一倍，zoom也增加一倍（当zoom为最大值时，zoom不再改变）。
        :param markers: 标注	使用规则见markers详细说明，标注最大数50个
        :param labels: 标签	使用规则见labels详细说明，标签最大数50个
        :param paths: 折线	使用规则见paths详细说明，折线和多边形最大数4个
        :param traffic: 交通路况标识	底图是否展现实时路况。 可选值： 0，不展现；1，展现。

        注：如果有标注/标签/折线等覆盖物，则中心点（location）和地图级别（zoom）可选填。当请求中无location值时，地图区域以包含请求中所有的标注/标签/折线的几何中心为中心点；如请求中无zoom，地图区域以包含请求中所有的标注/标签/折线为准，系统计算出zoom值。

markers

格式：
markers=markersStyle1:location1;location2..|markersStyle2:location3;location4..|markersStyleN:locationN;locationM..
location为经纬度信息，经纬度之间使用","分隔，不同的点使用";"分隔。 markersStyle可以使用系统提供的样式，也可以使用自定义图片。
系统marersStyle：label，font ,bold, fontSize，fontColor，background。

参数名称	说明	默认值
size	可选值： small,mid,large	small
color	选值范围：[0x000000, 0xffffff]
例如：
0x000000 black,
0x008000 green,
0x800080 purple,
0xFFFF00 yellow,
0x0000FF blue,
0x808080 gray,
0xffa500 orange,
0xFF0000 red,
0xFFFFFF white
0xFC6054
label	[0-9]、[A-Z]、[单个中文字] 当size为small时，图片不展现标注名。	无
markers示例： http://restapi.amap.com/v3/staticmap?markers=mid,0xFF0000,A:116.37359,39.92437;116.47359,39.92437&key=您的key 自定义markersStyle： -1，url，0。

-1表示为自定义图片，url为图片的网址。自定义图片只支持png格式。

markers示例 http://restapi.amap.com/v3/staticmap?markers=-1,http://ico.ooopic.com/ajax/iconpng/?id=158688.png,0:116.37359,39.92437&key=您的key

labels

格式：
labels=labelsStyle1:location1;location2..|labelsStyle2:location3;location4..|labelsStyleN:locationN;locationM..

location为经纬度信息，经纬度之间使用","分隔，不同的点使用";"分隔。

labelsStyle：label, font, bold, fontSize, fontColor, background。 各参数使用","分隔，如有默认值则可为空。

参数名称	说明	默认值
content	标签内容，字符最大数目为15	无
font	0：微软雅黑；
1：宋体；
2：Times New Roman;
3：Helvetica	0
bold	0：非粗体；
1：粗体	0
fontSize	字体大小，可选值[1,72]	10
fontColor	字体颜色，取值范围：[0x000000, 0xffffff]	0xFFFFFF
background	背景色，取值范围：[0x000000, 0xffffff]	0x5288d8
labels示例： http://restapi.amap.com/v3/staticmap?location=116.48482,39.94858&zoom=10&size=400*400&labels=朝阳公园,2,0,16,0xFFFFFF,0x008000:116.48482,39.94858&key=您的key

paths

格式： paths=pathsStyle1:location1;location2..|pathsStyle2:location3;location4..|pathsStyleN:locationN;locationM..
location为经纬度，经纬度之间使用","分隔，不同的点使用";"分隔。
pathsStyle：weight, color, transparency, fillcolor, fillTransparency。

参数名称	说明	默认值
weight	线条粗细。
可选值： [2,15]	5
color	折线颜色。 选值范围：[0x000000, 0xffffff]
例如：
0x000000 black,
0x008000 green,
0x800080 purple,
0xFFFF00 yellow,
0x0000FF blue,
0x808080 gray,
0xffa500 orange,
0xFF0000 red,
0xFFFFFF white	0x0000FF
transparency	透明度。
可选值[0,1]，小数后最多2位，0表示完全透明，1表示完全不透明。	1
fillcolor	多边形的填充颜色，此值不为空时折线封闭成多边形。取值规则同color	无
fillTransparency	填充面透明度。
可选值[0,1]，小数后最多2位，0表示完全透明，1表示完全不透明。	0.5
paths示例： http://restapi.amap.com/v3/staticmap?zoom=15&size=500*500&paths=10,0x0000ff,1,,:116.31604,39.96491;116.320816,39.966606;116.321785,39.966827;116.32361,39.966957&key=您的key

        """
        url = 'staticmap'
