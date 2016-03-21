var default_avatar = require('../static/img/hfut_badge.jpg');
var hfut_logo = require('../static/img/hfut_logo.png');
// 导航栏
var NavBar = React.createClass({
    // 状态初始化
    getInitialState: function () {
        return {avatar: default_avatar, stu_name: '无名氏'};
    },
    componentDidMount: function () {
        $('.ui .dropdown').dropdown();
        $('.sticky').sticky('refresh');
        // 这里没法触发 click 事件
        this.handleClick(document.getElementById(this.props.default_panel));
    },
    handleClick: function (target) {
        target = $(target);
        if (!target.hasClass('active')) {
            // 切换链接激活状态
            target.siblings('.item').removeClass('active');
            target.addClass('active');
            var animate_name = 'slide down';
            var panel_container = $('#panel_container');
            var component_will_exchanged = this.props.panels[target.attr('id')].component;
            if (panel_container.transition('is visible')) {
                // 如果有其他标签页，先用动画隐藏再卸载节点，然后挂载要显示的结点
                panel_container.transition(animate_name, {
                    onComplete: function () {
                        ReactDOM.unmountComponentAtNode(panel_container.get(0));
                        // 这里由于作用域不同不能使用this
                        ReactDOM.render(component_will_exchanged, panel_container.get(0));
                    }
                });
            }
            else {
                ReactDOM.render(component_will_exchanged, panel_container.get(0));
            }
            // 进入动画
            panel_container.transition(animate_name);
        }
    },
    onClick: function (e) {
        "use strict";
        this.handleClick(e.target);
    },
    render: function () {
        var navbar_items = [];
        for (var k in this.props.panels) {
            navbar_items.push(<a id={k} key={k} className="item"
                                 onClick={this.onClick}>{this.props.panels[k].name}</a>)
        }
        return (
            <div className="ui fixed top sticky menu">
                <div className="item">
                    <img src={hfut_logo} style={{width: 150+'px'}}/>
                </div>
                {navbar_items}
                <div className="right menu">
                    <div className="item">
                        <div className="ui transparent icon input">
                            <input placeholder="Search..." type="text"/>
                            <k className="search link icon"/>
                        </div>
                    </div>
                    <div className="ui dropdown link item">
                        <a className="dropdown link"><img className="ui avatar image"
                                                          src={this.state.avatar}/></a>
                        <div className="menu">
                            <div className="header">{this.state.stu_name}</div>
                            <div className="item">
                                个人中心
                            </div>
                            <div className="divider"></div>
                            <div className="item">
                                退出
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

module.exports = NavBar;