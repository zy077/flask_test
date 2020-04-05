var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 进入首页，加载新闻数据
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        // 记录点击选中的新闻分类id
        var clickCid = $(this).attr('data-cid');

        // 修改点击标签的选中样式
        // （1）删除所有的分类标签样式
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        // （2）给点击分类标签添加选中样式
        $(this).addClass('active');

        // 判断点击分类标签是否和当前分类标签相同
        if(clickCid != currentCid){
            // 更新分类id
            currentCid = clickCid;

            // 重置当前页参数
            cur_page = 1;
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {
        // 浏览器窗口高度（即滚动条高度）
        var window_height = $(window).height();

        // 网页高度
        var webpage_height = $(document).height();

        // 已经滚动了多少，这个是随着页面滚动实时变化的
        var scrolled_height = $(document).scrollTop();

        // 还可以滚动的高度
        var canscroll_height = webpage_height - (window_height + scrolled_height);

        // 可以滚动的高度小于100时，发起获取新数据的请求
        if(canscroll_height < 100){
            if(!data_querying){
                // 判断当前页是否小于总页数
                if(cur_page < total_page){
                    // 获取下一页数据
                    cur_page += 1;
                    data_querying = true;
                    updateNewsData();
                }
            }
        }

    })
})

function updateNewsData() {
    // TODO 更新新闻数据
    var param = {
        'cid': currentCid,
        'page': cur_page,
        // 'per_page': 50
    }
    $.get('/news_list', param, function (resp) {
        if(resp.errno == '0'){
            console.log(resp.data);
            // 查询数据结束，修改标记是否正在向后台获取数据的变量：data_querying
            data_querying = false;
            // 更新总页数标识
            total_page = resp.data.totalPage;

            // 当前页是第一页时，清空原来的数据
            if(cur_page == 1){
                $('.list_con').html('');
            }
            // 渲染后端返回的数据
            for(var i=0; i<resp.data.news_list.length; i++){
                var news = resp.data.news_list[i];
                var content = '<li>';
                content += '<a href="#" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>';
                content += '<a href="#" class="news_title fl">' + news.title + '</a>';
                content += '<a href="#" class="news_detail fl">' + news.digest + '</a>';
                content += '<div class="author_info fl">';
                content += '<div class="source fl">来源：' + news.source + '</div>';
                content += '<div class="time fl">' + news.create_time + '</div>';
                content += '</div>';
                content += '</li>';
                $('.list_con').append(content)
            }
        }
        else{
            // 查询数据失败
            alert('查询数据失败！')
        }
    })
}
