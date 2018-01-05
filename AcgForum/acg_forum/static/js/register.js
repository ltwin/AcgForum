/**
 * Created by ltwin on 2017/12/30.
 */
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $('#form-register').submit(function (e) {
        e.preventDefault();

    })
});
