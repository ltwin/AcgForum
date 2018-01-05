/**
 * Created by ltwin on 2017/12/28.
 */

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $.ajax({
        url: "/api/v1.0/index",
        type: "GET",
        contentType: "application/json",
        // data: JSON.stringify(req),
        headers: {"X-CSRFToken": getCookie("csrf_token")},
        dataType: 'json',
        success: function (resp) {
            // alert(resp);
            // alert(resp.username);
            // alert(resp.mobile);
            // alert('success');
            if (resp.errno == '4001'){
                // alert('4001');
                $('ul li').html('数据异常');
            }
            else if (resp.errno == '4101'){
                // alert('4101');
                $('ul li').hide();
                $('.errmsg').html('用户未登录')
            }
            else if (resp.errno == '0'){
                // alert('0');
                // alert(resp.username);
                $('ul #username').html(resp.data.username);
                // $('ul #password').html(resp.data.password);
                $('ul #mobile').html(resp.data.mobile);
            }
        }
    })
});
