// 统计面板

//<img src="http://semantic-ui.com/images/avatar2/large/kristy.png" />
var StatisticsPanel = React.createClass({
    componentDidMount: function () {
        "use strict";
        $('.ui.accordion').accordion();
    },
    render: function () {
        return (
            <div className="ui small card">
                <div className="content">
                    <div className="header">
                        <img className="ui avatar image" src="http://172.18.6.98/student/photo/2013/2013217413.JPG"/>
                        周而良
                        <i className="small man icon"></i>
                    </div>
                </div>
                <div className="content">
                        <p>13电信一班</p>
                        安徽省安庆市宿松县
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

module.exports = StatisticsPanel;