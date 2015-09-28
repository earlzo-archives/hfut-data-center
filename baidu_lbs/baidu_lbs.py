# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import hashlib
import inspect
import urllib
import time

import requests

# todo: api 尚未完成测试， sn 计算存在很大问题
__all__ = ['LbsApi', 'LbsSearch', 'LbsStorage']


class LbsBase(object):
    HOST = 'http://api.map.baidu.com'

    def __init__(self, ak, sk=None):
        self.ak = ak
        self.sk = sk

    def generate_sn(self, method, relative_url, ori_params, add_timestamp=False):
        method = method.lower()
        ori_params['ak'] = self.ak
        if add_timestamp:
            ori_params['timestamp'] = int(time.time() * 1000)
        # 对请求参数排序, 保证在 POST 时也能使用
        params = sorted(ori_params.iteritems())
        query_str = ''.join(
            [relative_url, '?',
             '&'.join([''.join([k, '=', str(v)]) for k, v in params if v])]
        )
        # 对 query_str 进行转码, safe内的保留字符不转换
        # 如 /geocoder/v2/?address=百度大厦&output=json&ak=your_ak
        encoded_str = urllib.quote(query_str.encode(), safe="/:=&?#+!$,;'@()*[]".encode()).decode()
        if method == 'get':
            url = ''.join([self.HOST, encoded_str])
        elif method == 'post':
            url = ''.join([self.HOST, relative_url])
        else:
            raise ValueError('{:s} is a wrong method!'.format(method))

        if self.sk:
            # 在最后直接追加上 sk
            raw_str = encoded_str + self.sk
            sn = hashlib.md5(urllib.quote_plus(raw_str)).hexdigest()
            if method == 'post':
                ori_params['sn'] = sn
            elif method == 'get':
                url = ''.join([url, '&sn=', sn])
        return ori_params, url

    def get_response(self, method, relative_url, ori_params, files=None, add_timestamp=False):
        data, url = self.generate_sn(method, relative_url, ori_params, add_timestamp)
        method = method.lower()
        if method == 'get':
            res = requests.get(url, allow_redirects=False).json()
        elif method == 'post':
            res = requests.post(url, data=data, files=files, allow_redirects=False).json()
        else:
            raise ValueError('{:s} is a wrong method!'.format(method))

        if res['status'] == 0:
            return res
        else:
            raise ValueError(str(res))


class LbsStorage(LbsBase):
    def create_geotable(self, name, geotype=1, is_published=1, add_timestamp=False):
        """
        创建表
        :param name: geotable的中文名称 string(45) 必选
        :param geotype: geotable持有数据的类型 int32	必选 1：点；2：线；3：面。默认为1（当前只支持点）
        :param is_published: 是否发布到检索 int32 必选 0：未自动发布到云检索，1：自动发布到云检索；
                             策略提示：
                             注：1）通过URL方式创建表时只有is_published=1时 在云检索时表内的数据才能被检索到。
                                2）可通过数据管理模块设置，如图所示，在设置中将是否发送到检索一栏中选定为是即可。
        :param add_timestamp: 是否添加时间戳验证
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/geotable/create'
        ori_params = {
            'name': name,
            'geotype': geotype,
            'is_published': is_published
        }
        return self.get_response('post', relative_url, ori_params, add_timestamp=add_timestamp)

    def list_geotable(self, name=None):
        """
        查询
        :param name: geotable的名字 string(45) 可选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/geotable/list'
        ori_params = {
            'name': name
        }
        return self.get_response('get', relative_url, ori_params)

    def detail_geotable(self, id):
        """
        查询指定id表
        :param id: 指定geotable的id int32 必选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/geotable/detail'
        ori_params = {
            'id': id
        }
        return self.get_response('get', relative_url, ori_params)

    def update_geotable(self, id, is_published, name=None):
        """
        修改表
        :param id: geotable主键	uint32	必选
        :param is_published: 是否发布到检索	int32	会引起批量操作
        :param name: geotable的中文名称	string(45)	可选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/geotable/update'
        ori_params = {
            'id': id,
            'name': name,
            'is_published': is_published
        }
        return self.get_response('post', relative_url, ori_params)

    def delete_geotable(self, id):
        """
        删除表, 当geotable里面没有有效数据时, 才能删除geotable
        :param id: 表主键	uint32	必选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/geotable/delete'
        ori_params = {
            'id': id
        }
        return self.get_response('post', relative_url, ori_params)

    def create_column(self, geotable_id, name, key, column_type,
                      default_value=None,
                      max_length=2048,
                      is_sortfilter_field=0,
                      is_search_field=0,
                      is_index_field=0,
                      is_unique_field=0):
        """
        创建列
        :param geotable_id: 所属于的geotable_id
        :param name: column的属性中文名称	string(45)	必选
        :param key: column存储的属性key	string(45)	必选，同一个geotable内的名字不能相同
        :param column_type: 存储的值的类型	uint32	必选，枚举值1:Int64, 2:double, 3:string, 4:在线图片url
        :param max_length: 最大长度	uint32	最大值2048，最小值为1，针对string有效，并且string时必填。此值代表utf8的汉字个数，不是字节个数
        :param default_value: 默认值	string(45)	设置默认值
        :param is_sortfilter_field: 是否检索引擎的数值排序筛选字段	uint32	必选 1代表是，0代表否。设置后效果详见 LBS云检索最多只能设置15个,只有int或者double类型可以设置
        :param is_search_field: 是否检索引擎的文本检索字段	uint32	必选 1代表支持，0为不支持。只有string可以设置检索字段只能用于字符串类型的列且最大长度不能超过512个字节
        :param is_index_field: 是否存储引擎的索引字段	uint32	必选 用于存储接口查询:1代表支持，0为不支持 注：is_index_field=1 时才能在根据该列属性值检索时检索到数据
        :param is_unique_field: 可选，用于更新，删除，查询：1代表支持 ，0为不支持
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/column/create'

        # 无效参数将不会进入 sn 的计算
        if column_type not in (1, 2):
            is_sortfilter_field = None

        if column_type != 3:
            max_length = None
            is_search_field = None

        ori_params = {
            'geotable_id': geotable_id,
            'name': name,
            'key': key,
            'type': column_type,
            'max_length': max_length,
            'default_value': default_value,
            'is_sortfilter_field': is_sortfilter_field,
            'is_search_field': is_search_field,
            'is_index_field': is_index_field,
            'is_unique_field': is_unique_field
        }
        return self.get_response('post', relative_url, ori_params)

    def list_column(self, geotable_id, name=None, key=None):
        """
        查询列
        :param name: name	geotable meta的属性中文名称	string(45)	可选
        :param key: key	geotable meta存储的属性key	string(45)	可选
        :param geotable_id: geotable_id	所属于的geotable_id	string(50)	必选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/column/list'
        ori_params = {
            'geotable_id': geotable_id,
            'name': name,
            'key': key
        }
        return self.get_response('get', relative_url, ori_params)

    def detail_column(self, geotable_id, id):
        """
        查询指定id列
        :param id: id	列的id	uint32	必选
        :param geotable_id: geotable_id	表的id	uint32	必选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/column/detail'
        ori_params = {
            'geotable_id': geotable_id,
            'id': id
        }
        return self.get_response('get', relative_url, ori_params)

    def update_column(self, geotable_id, id,
                      name=None,
                      default_value=None,
                      max_length=2048,
                      is_sortfilter_field=0,
                      is_search_field=0,
                      is_index_field=0,
                      is_unique_field=0):
        """
        修改指定条件列
        :param id: id	列主键	uint32	必选
        :param geotable_id: geotable_id	所属表主键	uint32	必选
        :param name: name	属性中文名称	string(45)	可选
        :param default_value: default_value	默认值	string	可选
        :param max_length: max_length	文本最大长度	int32	字符串最大长度，只能改大，不能改小
        :param is_sortfilter_field: 是否检索引擎的数值排序字段	uint32	1代表是，0代表否，可能会引起批量操作
        :param is_search_field: 是否检索引擎的文本检索字段	uint32	1代表是，0代表否，会引起批量操作
        :param is_index_field: 是否存储引擎的索引字段	uint32	1代表是，0代表否
        :param is_unique_field: 是否存储索引的唯一索引字段	uint32	1代表是，0代表否
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/column/update'
        ori_params = {
            'geotable_id': geotable_id,
            'id': id,
            'name': name,
            'max_length': max_length,
            'default_value': default_value,
            'is_sortfilter_field': is_sortfilter_field,
            'is_search_field': is_search_field,
            'is_index_field': is_index_field,
            'is_unique_field': is_unique_field
        }
        return self.get_response('post', relative_url, ori_params)

    def delete_column(self, geotable_id, id):
        """
        删除指定条件列
        :param id:
        :param geotable_id:
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/column/delete'
        ori_params = {
            'geotable_id': geotable_id,
            'id': id
        }
        return self.get_response('post', relative_url, ori_params)

    def create_poi(self, geotable_id, latitude, longitude,
                   coord_type=3,
                   title=None,
                   address=None,
                   tags=None,
                   **kwargs):
        """
        创建数据
        :param title: poi名称	string(256)	可选
        :param address: 地址	string(256)	可选
        :param tags: tags	string(256)	可选
        :param latitude: 用户上传的纬度	double	必选
        :param longitude: 用户上传的经度	double	必选
        :param coord_type: 用户上传的坐标的类型	uint32	必选
                           1：GPS经纬度坐标
                           2：国测局加密经纬度坐标
                           3：百度加密经纬度坐标
                           4：百度加密墨卡托坐标
        :param geotable_id: 记录关联的geotable的标识	string(50)	必选，加密后的id
        :**kwargs: 用户在column定义的key/value对	开发者自定义的类型（string、int、double）	唯一索引字段必选，且需要保证唯一，否则会创建失败
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/poi/create'
        ori_params = {
            'geotable_id': geotable_id,
            'title': title,
            'address': address,
            'tags': tags,
            'latitude': latitude,
            'longitude': longitude,
            'coord_type': coord_type
        }
        ori_params.update(**kwargs)
        return self.get_response('post', relative_url, ori_params)

    def list_poi(self, geotable_id, title=None, tags=None, bounds=None, page_index=0, page_size=10, **kwargs):
        """
        查询指定条件的数据
        :param geotable_id: geotable_id	string(50)	必选
        :param title: 记录（数据）名称	string(256)	可选
        :param tags: 记录的标签（用于检索筛选）	string(256)	可选
        :param bounds: 查询的矩形区域	string(100)	格式x1,y1;x2,y2分别代表矩形的左上角和右下角，可选
        :param page_index: 分页索引	uint32	默认为0，最大为9
        :param page_size: 分页数目	uint32	默认为10，上限为200
        :**kwargs: 用户在column定义的key/value对
                   column需要设置了is_index_field=1。对于string，是两端匹配。
                   对于int或者double，则是范围查找，传递的格式为最小值,最大值。
                   当无最小值或者最大值时，用-代替，同时，此字段最大长度不超过50，最小值与最大值都是整数
                   例：如加入一个命名为color数据类型为string的column，在检索是可设置为“color=red”的形式来检索color字段为red的POI
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/poi/list'
        ori_params = {
            'geotable_id': geotable_id,
            'title': title,
            'tags': tags,
            'bounds': bounds,
            'page_index': page_index,
            'page_size': page_size
        }
        ori_params.update(**kwargs)
        return self.get_response('get', relative_url, ori_params)

    def detail_poi(self, geotable_id, id):
        """
        查询指定id的数据
        :geotable_id: 表主键	int32	必选
        :id: poi主键	uint64	必选
        """
        relative_url = '/geodata/v3/poi/detail'
        ori_params = {
            'geotable_id': geotable_id,
            'id': id
        }
        return self.get_response('get', relative_url, ori_params)

    def update_poi(self, geotable_id, id, coord_type,
                   latitude=None,
                   longitude=None,
                   title=None,
                   address=None,
                   tags=None,
                   **kwargs):
        """
        修改数据
        :param geotable_id: 记录关联的geotable的标识	string(50)	必选，加密后的id
        :param id: poi的id	uint64	当不存在唯一索引字段时必须，存在唯一索引字段可选
        :param title: poi名称	string(256)	可选
        :param address: 地址	string(256)	可选
        :param tags: tags	string(256)	可选
        :param latitude: 用户上传的纬度	double	可选
        :param longitude: 用户上传的经度	double	可选
        :param coord_type: 用户上传的坐标的类型	uint32	必选
                           1：GPS经纬度坐标
                           2：国测局加密经纬度坐标
                           3：百度加密经纬度坐标
                           4：百度加密墨卡托坐标
        :**kwargs: 用户在column定义的key/value对	开发者自定义的类型（string、int、double）
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/poi/update'
        ori_params = {
            'geotable_id': geotable_id,
            'id': id,
            'title': title,
            'address': address,
            'tags': tags,
            'latitude': latitude,
            'longitude': longitude,
            'coord_type': coord_type
        }
        ori_params.update(**kwargs)
        return self.get_response('post', relative_url, ori_params)

    def delete_poi(self, geotable_id, id,
                   ids=None,
                   title=None,
                   tags=None,
                   bounds=None,
                   is_total_del=0,
                   **kwargs):
        """
        删除数据
        :param geotable_id: 记录关联的geotable的标识	string(50)	必选，加密后的id
        :param id: poi的id	uint64	当不存在唯一索引字段时必须，存在唯一索引字段可选
        :param title: poi名称	string(256)	可选
        :param tags: tags	string(256)	可选
        :param bounds: 查询的矩形区域	string(100)	格式x1,y1;x2,y2分别代表矩形的左上角和右下角
        :param is_total_del: 标记为批量删除	int32	如果是批量删除，则需要传这个参数，值为1；如果不是批量删除，则不用传这个参数
        :**kwargs: 用户在column定义的key/value对	开发者自定义的类型（string、int、double）
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/poi/delete'
        if not is_total_del:
            is_total_del = None
        ori_params = {
            'geotable_id': geotable_id,
            'id': id,
            'ids': ids,
            'title': title,
            'tags': tags,
            'bounds': bounds,
            'is_total_del': is_total_del
        }
        ori_params.update(**kwargs)
        return self.get_response('post', relative_url, ori_params)

    def post_pois_csv_file(self, geotable_id, poi_list):
        """
        批量上传数据

        导入文件（poi_list）的CSV格式
        参数名	参数含义	类型	备注
        title	poi名称	string(45)	必选
        latitude	用户上传的纬度	double	必选
        longitude	用户上传的经度	double	必选
        coord_type	用户上传的坐标的类型	uint32	1.GPS经纬度坐标
                                                2.国测局加密经纬度坐标
                                                3.百度加密经纬度坐标
                                                4.百度加密墨卡托坐标
        {column key} 	用户在column定义的key/value对 	用户自定义的类类别 	可选
        address	地址	string（256）	可选

        :param geotable_id: 导入的geotable的标识	uint32	必选
        :param poi_list: 输入的poi列表名称	file	必选，小于10M
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/poi/upload'
        ori_params = {
            'geotable_id': geotable_id
        }
        files = {
            'poi_list': open(poi_list, 'rb')
        }
        return self.get_response('post', relative_url, ori_params, files=files, add_timestamp=True)

    def list_import_data(self, geotable_id, job_id, status=0, page_index=0, page_size=10, timestamp=False):
        """
        批量上传进度查询接口
        :param geotable_id: 导入的geotable的标识	uint32	必选
        :param job_id: 导入接口返回的job_id 	string（50）	必选
        :param status: Poi导入的状态	uint32	默认为0，0为全部，1为失败，2为成功
        :param page_index: 分页索引	uint32	默认为0
        :param page_size: 分页数目	uint32	默认为10，上限为100
        :param timestamp: 时间戳	uint32
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/job/listimportdata'
        ori_params = {
            'geotable_id': geotable_id,
            'job_id': job_id,
            'status': status,
            'page_index': page_index,
            'page_size': page_size
        }
        return self.get_response('get', relative_url, ori_params, add_timestamp=timestamp)

    def list_job(self, job_type=None, status=None):
        """
        批量操作任务查询
        :param job_type: type	job类型	int32(<10)
        :param status: job状态	int32(<10)	1为新增，2为正在处理，3为完成。
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/job/list'
        ori_params = {
            'type': job_type,
            'status': status
        }
        return self.get_response('get', relative_url, ori_params)

    def detail_job(self, id):
        """
        根据id查询批量任务
        :param id: id	uint64	必选
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geodata/v3/job/detail'
        ori_params = {
            'id': id
        }
        return self.get_response('get', relative_url, ori_params)


class LbsSearch(LbsBase):
    def nearby_search(self, geotable_id, location, q=None, coord_type=3, radius=1000, tags=None, sortby=None,
                      filter=None, page_index=0, page_size=10):
        """
        poi周边搜索
        :param geotable_id: geotable主键	uint32	数字	必须
        :param location: 检索的中心点	string(25)	逗号分隔的经纬度	必须
                             样例：116.4321,38.76623
        :param q: 检索关键字	string(45)	任意汉字或数字，英文字母，可以为空字符	可选
        :param coord_type: 坐标系	uint32	数字	可选
                           3代表百度经纬度坐标系统 4代表百度墨卡托系统
        :param radius: 检索半径	uint32	单位为米，默认为1000	可选
        :param tags: 标签	string(45)	空格分隔的多字符串	可选
                         样例：美食 小吃
        :param sortby: 排序字段	string	”分隔的多个检索条件。
                       格式为sortby={key1}:value1|{key2:val2|key3:val3}。
                       最多支持16个字段排序 {keyname}:1 升序 {keyname}:-1 降序
                       以下keyname为系统预定义的： distance 距离排序 weight 权重排序
                       可选
                       默认为按weight排序 如果需要自定义排序则指定排序字段
                       样例：按照价格由便宜到贵排序 sortby=price:1
        :param filter: 过滤条件	string(50)	竖线分隔的多个key-value对
                       key为筛选字段的名称(存储服务中定义) 支持连续区间或者离散区间的筛选：
                       a:连续区间 key:value1,value2 b:离散区间 key:[value1,value2,value3,...]
                       可选
                       样例:
                           a:连续区间 筛选价格为9.99到19.99并且生产时间为2013年的项 price:9.99,19.99|time:2012,2012
                           b:离散区间 筛选价格为8,9,13，并且生产时间为2013年的项 price:[8,9,13]|time:2012,2012
                           注：符号为英文半角中括号
        :param page_index: 分页索引	uint32	当前页标，从0开始	可选 默认为0
        :param page_size: 分页数量	uint32	当前页面最大结果数	可选 默认为10，最多为50
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geosearch/v3/nearby'
        ori_params = inspect.getcallargs(self.nearby_search, geotable_id, location, q, coord_type, radius, tags,
                                         sortby, filter, page_index, page_size)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)

    def local_search(self, geotable_id, q, coord_type=3, region=None, tags=None, sortby=None, filter=None, page_index=0,
                     page_size=10):
        """
        poi本地搜索
        :param geotable_id: geotable主键	uint32	数字	必须
        :param q: 检索关键字	string(45)	任意汉字或数字，英文字母，可以为空字符 必须
        :param coord_type: 坐标系	uint32	数字	可选
                           3代表百度经纬度坐标系统 4代表百度墨卡托系统
        :param region: 检索区域名称	String(25)	市或区的名字，如北京市，海淀区。	可选
                       此接口推荐填写该参数, 否则，默认按照全国范围来检索
        :param tags: 标签	string(45)	空格分隔的多字符串	可选
                         样例：美食 小吃
        :param sortby: 排序字段	string	”分隔的多个检索条件。
                       格式为sortby={key1}:value1|{key2:val2|key3:val3}。
                       最多支持16个字段排序 {keyname}:1 升序 {keyname}:-1 降序
                       以下keyname为系统预定义的： distance 距离排序 weight 权重排序
                       可选
                       默认为按weight排序 如果需要自定义排序则指定排序字段
                       样例：按照价格由便宜到贵排序 sortby=price:1
        :param filter: 过滤条件	string(50)	竖线分隔的多个key-value对
                       key为筛选字段的名称(存储服务中定义) 支持连续区间或者离散区间的筛选：
                       a:连续区间 key:value1,value2 b:离散区间 key:[value1,value2,value3,...]
                       可选
                       样例:
                           a:连续区间 筛选价格为9.99到19.99并且生产时间为2013年的项 price:9.99,19.99|time:2012,2012
                           b:离散区间 筛选价格为8,9,13，并且生产时间为2013年的项 price:[8,9,13]|time:2012,2012
                           注：符号为英文半角中括号
        :param page_index: 分页索引	uint32	当前页标，从0开始	可选 默认为0
        :param page_size: 分页数量	uint32	当前页面最大结果数	可选 默认为10，最多为50
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geosearch/v3/local'
        ori_params = inspect.getcallargs(self.local_search, geotable_id, q, coord_type, region, tags, sortby,
                                         filter, page_index, page_size)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)

    def bound_search(self, geotable_id, q, bound, coord_type=3, tags=None, sortby=None, filter=None, page_index=0,
                     page_size=10):
        """
        poi矩形检索
        :param geotable_id: geotable主键	uint32	数字	必须
        :param q: 检索关键字	string(45)	任意汉字或数字，英文字母，可以为空字符 必须
        :param bound: 矩形区域	String(25)	左下角和右上角的经纬度坐标点。2个点用;号分隔	必须
                      样例：116.30,36.20;117.30,37.20
        :param coord_type: 坐标系	uint32	数字	可选
                           3代表百度经纬度坐标系统 4代表百度墨卡托系统
        :param tags: 标签	string(45)	空格分隔的多字符串	可选
                         样例：美食 小吃
        :param sortby: 排序字段	string	”分隔的多个检索条件。
                       格式为sortby={key1}:value1|{key2:val2|key3:val3}。
                       最多支持16个字段排序 {keyname}:1 升序 {keyname}:-1 降序
                       以下keyname为系统预定义的： distance 距离排序 weight 权重排序
                       可选
                       默认为按weight排序 如果需要自定义排序则指定排序字段
                       样例：按照价格由便宜到贵排序 sortby=price:1
        :param filter: 过滤条件	string(50)	竖线分隔的多个key-value对
                       key为筛选字段的名称(存储服务中定义) 支持连续区间或者离散区间的筛选：
                       a:连续区间 key:value1,value2 b:离散区间 key:[value1,value2,value3,...]
                       可选
                       样例:
                           a:连续区间 筛选价格为9.99到19.99并且生产时间为2013年的项 price:9.99,19.99|time:2012,2012
                           b:离散区间 筛选价格为8,9,13，并且生产时间为2013年的项 price:[8,9,13]|time:2012,2012
                           注：符号为英文半角中括号
        :param page_index: 分页索引	uint32	当前页标，从0开始	可选 默认为0
        :param page_size: 分页数量	uint32	当前页面最大结果数	可选 默认为10，最多为50
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geosearch/v3/bound'
        ori_params = inspect.getcallargs(self.bound_search, geotable_id, q, bound, coord_type, tags, sortby,
                                         filter, page_index, page_size)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)

    def poi_detail(self, geotable_id, id, coord_type=3):
        """
        poi详情检索
        :param geotable_id: geotable主键	uint32	数字	必须
        :param id: poi点的id值
        :param coord_type: 坐标系	uint32	数字	可选
                           3代表百度经纬度坐标系统 4代表百度墨卡托系统
        :return: 转换成字典对象的的 json 响应
        """
        relative_url = '/geosearch/v3/detail/' + str(id)
        ori_params = inspect.getcallargs(self.poi_detail, self, geotable_id, id, coord_type)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)


class LbsApi(LbsBase):
    def geocoding(self, address, city=None, output='json'):
        relative_url = '/geocoder/v2/'
        ori_params = inspect.getcallargs(self.geocoding, address, city, output)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)

    def ungeocoding(self, location, coordtype='bd09ll', pois=0, output='json'):
        relative_url = '/geocoder/v2/'
        ori_params = inspect.getcallargs(self.ungeocoding, location, coordtype, pois, output)
        ori_params.pop('self')
        return self.get_response('get', relative_url, ori_params)
