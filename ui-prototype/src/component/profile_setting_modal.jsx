define(['jquery', 'react'], function ($, React) {
    var ProfileModal = React.createClass({
        // 状态初始化
        getInitialState: function () {
            return {avatar: 'img/hfut_badge.jpg', stu_name: '无名氏'};
        },
        render: function () {

            return (

                <div id='profile_modal' className="ui modal">
                    <div className="header">资料</div>
                    <div className="content">资料</div>
                    <div class="actions">
                        <div class="ui black deny button">
                            Nope
                        </div>
                        <div class="ui positive right labeled icon button">
                            Yep, that's me
                            <i class="checkmark icon"></i>
                        </div>
                    </div>
                </div>
            );
        }
    });
});