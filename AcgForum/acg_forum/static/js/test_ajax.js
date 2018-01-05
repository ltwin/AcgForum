/**
 * Created by ltwin on 2017/12/28.
 */

// importScripts('/static')
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === 'function'){
        d += performance.now();
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function () {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid
}

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCodeID() {
    // 生成一个编号
    // 使用uuid保证编号唯一
    imageCodeId = generateUUID();

    // 设置页面中图片验证码img标签的src属性
    var imageCodeUrl = "/api/v1.0/image_code/" + imageCodeId;
    $(".image-code>img").attr("src", imageCodeUrl);
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phoneCode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phoneCode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phoneCode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    //
    var req = {
        text: imageCode, // 用户填写的图片验证码
        id: imageCodeId // 图片验证码的编号
    };
    $.get("/api/v1.0/sms_code/"+mobile, req, function (resp) {
        // 表示后端发送短信成功
        if (resp.errno == "0") {
            // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
            var num = 60;
            // 设置一个计时器
            var t = setInterval(function () {
                if (num == 1) {
                    // 如果计时器到最后, 清除计时器对象
                    clearInterval(t);
                    // 将点击获取验证码的按钮展示的文本回复成原始文本
                    $(".phoneCode-a").html("获取验证码");
                    // 将点击按钮的onclick事件函数恢复回去
                    $(".phoneCode-a").attr("onclick", "sendSMSCode();");
                } else {
                    num -= 1;
                    // 展示倒计时信息
                    $(".phoneCode-a").html(num+"秒");
                }
            }, 1000, 60)
        } else {
            // 表示后端出现了错误，可以将错误信息展示到前端页面中
            $("#phone-code-err span").html(resp.errmsg);
            $("#phone-code-err").show();
            // 将点击按钮的onclick事件函数恢复回去
            $(".phoneCode-a").attr("onclick", "sendSMSCode();");
        }

    }, "json");

}

$(function () {
    generateImageCodeID();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imageCode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phoneCode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $('.form-register').submit(function (e) {
        e.preventDefault();
        // console.log('test');
        // alert('test');
        var mobile = $('#mobile').val();
        var phoneCode = $('#phoneCode').val();
        var password = $('#password').val();
        var password2 = $('#password2').val();

        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        var req = {
            "mobile": mobile,
            "password": password,
            'sms_code': phoneCode
        };

        $.ajax({
            url: "/api/v1.0/test",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(req),
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            dataType: 'json',
            success: function (resp) {
                // alert(resp.errno);
                // alert('success');
                if (resp.errno == "0"){
                    // alert('0');
                    location.href = "/index.html";
                }
                else if (resp.errno == "4101"){
                    // alert('4101');
                    location.href = '/login.html';
                }
                else {
                    // alert('error');
                    $("#password2-err span").html(resp.errmsg);
                    $("#password2").show();
                }
            }
        })
    })
});