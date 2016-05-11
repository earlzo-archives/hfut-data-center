"use strict";
var MapInfoWindow = React.createClass({
    getInitialState: function () {
        // todo: 初始化时从服务器获取数据
        return {
            avatar: 'http://172.18.6.98/student/photo/2013/2013217413.JPG',
            name: '周而良',
            klass: '13电信一班',
            address: '安徽省安庆市宿松县'
        }
    },
    render: function () {
        // todo: 数据获取功能完成后需要修改组件
        return (
            <div className="ui small card">
                <div className="content">
                    <div className="header">
                        <img className="ui avatar image"
                             src={this.state.avatar}/>
                        {this.state.name} {this.props.id}
                        <i className="small man icon"></i>
                    </div>
                </div>
                <div className="content">
                    <p>{this.state.klass}</p>
                    {this.state.address}
                </div>
                <div className="extra content">
                    <div className="ui accordion">
                        <div className="title">
                            <i className="dropdown icon"></i>
                            更多信息
                        </div>
                        <div className="content">
                            <div className="ui animated divided list transition hidden">
                                <div className="item">
                                    <i className="birthday icon"></i>
                                    <div className="content">
                                        1995年2月
                                    </div>
                                </div>
                                <div className="item">
                                    <i className="birthday icon"></i>
                                    <div className="content">
                                        A poodle, its pretty basic
                                    </div>
                                </div>
                                <div className="item">
                                    <i className="birthday icon"></i>
                                    <div className="content">
                                        He's also a dog
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
});

// 地图面板
var MapPanel = React.createClass({
    initMap: function () {
        //var panel_containter = $('#'+ this.props.panel_id);
        var panel_containter = $('#a_map_container');
        var navbar = $('#navbar_container');
        console.log(navbar.height());
        //map_tag.css('margin-top', nav_tag.height());
        panel_containter.width(window.innerWidth);

        panel_containter.height(window.innerHeight - navbar.height());
        console.log('分段高度为:' + panel_containter.height());
        window.onresize = function () {
            panel_containter.width(window.innerWidth);
            panel_containter.height(window.innerHeight - navbar.height());
        };
        //初始化地图实例, 默认定位到学校
        var map = new AMap.Map('a_map_container', {zoom: 10, center: [118.706665, 30.897888]});
        // 创建地址解析器实例，若用户登录则将焦点定位到自己的地址，否则定位到学校
        //AMap.service(["AMap.Geocoder"], function () { //加载地理编码
        //    var geocoder = new AMap.Geocoder();
        //    //步骤三：通过服务对应的方法回调服务返回结果，本例中通过逆地理编码方法getAddress回调结果
        //    geocoder.getLocation('合肥工业大学（宣城校区）', function (status, result) {
        //        //根据服务请求状态处理返回结果
        //        if (status == 'error') {
        //            alert("服务请求出错啦！ ");
        //        }
        //        if (status == 'no_data') {
        //            alert("无数据返回，请换个关键字试试～～");
        //        }
        //        else {
        //            console.log(result);
        //            map.setZoom(10);
        //            map.setCenter(result.location);
        //        }
        //    });
        //});
        // 地图类型控件 http://lbs.amap.com/api/javascript-api/reference/plugin/#AMap.MapType
        map.plugin(["AMap.MapType"], function () {
            //地图类型切换
            var type = new AMap.MapType({
                defaultType: 0 //使用2D地图
            });
            map.addControl(type);
        });
        // 比例尺控件
        map.plugin(["AMap.Scale"], function () {
            var scale = new AMap.Scale();
            map.addControl(scale);
        });
        // 工具条控件 http://lbs.amap.com/api/javascript-api/reference/plugin/#AMap.ToolBar
        map.plugin(["AMap.ToolBar"], function () {
            //加载工具条
            var tool = new AMap.ToolBar({direction: false, autoPosition: false});
            map.addControl(tool);
        });
        console.log('图层加载开始！');
        //添加数据图层 http://lbs.amap.com/api/javascript-api/reference/layer/#MassMarks
        var mass_marks = new AMap.MassMarks(
            // todo: 初始化时向使用url服务器请求数据
            [{lnglat: [118.706665, 30.897888], id: 2013217413, naame: '周而良'}],
            {
                // 必填参数，图标显示位置偏移量，以图标的左上角为基准点（0,0）点
                anchor: new AMap.Pixel(5, 5),
                // 必填参数,图标的地址
                url: 'http://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
                // 必填参数，图标的尺寸
                size: new AMap.Size(11, 11)
            });
        mass_marks.on('click', function (point) {
            var info_window = new AMap.InfoWindow({
                isCustom: true,
                closeWhenClickMap: true,
                autoMove: true,
                content: ReactDOMServer.renderToString(<MapInfoWindow id={point.data.id}/>)
            });
            info_window.on('open', function () {
                // DOM没有立即刷新，简直坑爹
                window.setTimeout(function () {
                    $('.ui.accordion').accordion('refresh');
                }, 100);
            });
            info_window.open(map, point.data.lnglat);
        });
        console.log('图层声明成功！');
        // 海量点加载完成事件
        mass_marks.setMap(map);
        console.log('图层加载完成！');
    },
    componentDidMount: function () {
        "use strict";
        console.log("组件挂载成功！");
        // 使用ReactDOM渲染script元素无法执行, 而百度地图API不能直接引用文件
        var script = document.createElement('script');
        script.src = this.props.api_url;
        $('#a_map_container').before(script);
        //this.forceUpdate();
        // 将回调函数添加到全局空间
        window.initMap = this.initMap;
    },
    componentWillUnmount: function () {
        // 注销地图初始化函数
        delete window.initMap;
    },
    render: function () {
        return (
            <div>
                <div id="a_map_container"></div>
            </div>
        )
    }
});

module.exports = MapPanel;