require('../semantic/dist/semantic.min.js');
require('../semantic/dist/semantic.min.css');

var NavBar = require('./component/main_frame.jsx');
var MapPanel = require('./component/map_panel.jsx');
var StatisticsPanel = require('./component/statistics_panel.jsx');
var panels = {
    map: {
        name: '地图',
        //component: <MapPanel panel_id="panel_container" api_url="http://api.map.baidu.com/api?v=2.0&ak=7tf5jn5zGAPG4Pn7mKFjNws1&callback=initMap"/>
        component: <MapPanel panel_id="panel_container"
                             api_url="http://webapi.amap.com/maps?v=1.3&key=b23838665fe452ac668009c4099bf4c6&callback=initMap"/>
    },
    statistics: {
        name: '统计',
        component: <StatisticsPanel />
    }
};
ReactDOM.render(
    (
        <div className="ui segment">
            <div className="ui active dimmer">
                <div className="ui text loader">Loading</div>
            </div>
        </div>),
    document.getElementById('navbar_container')
);

ReactDOM.render(
    <NavBar panels={panels} default_panel='map'/>,
    document.getElementById('navbar_container')
);
