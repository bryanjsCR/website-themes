odoo.define('facebook_instant_article.facebook_instant_article', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');

    function checkArticleImportStatus(fb_import_id) {
        console.log(fb_import_id);
        ajax.jsonRpc('/fb_instant_article/check_import', 'call', {'fb_import_id': fb_import_id})
            .then(function(data){
                if (data === true) {
                    $("span[id='fb_import_ok']").show();
                    return true;
                } else {
                    $("span[id='fb_import_ok']").hide();
                    return false;
                }
            });
    }
    var check_timer;

    $(document).ready(function () {
        var $fb_import_id = $("input[name='fb_import_id']");
        if (typeof $fb_import_id === 'undefined'){
            return;
        }
        if (typeof $fb_import_id.val() === 'undefined'){
            return;
        }
        if($fb_import_id.val() !== ""){
            //check import status
            var import_status = checkArticleImportStatus($fb_import_id.val());
            if (import_status != true) {
                check_timer = window.setInterval(function () {
                    var $fb_import_id = $("input[name='fb_import_id']");
                    ajax.jsonRpc('/fb_instant_article/check_import', 'call', {'fb_import_id': $fb_import_id.val()})
                        .then(function(data){
                            if (data === true) {
                                $("span[id='fb_import_ok']").show();
                                if (typeof check_timer != undefined){
                                    window.clearInterval(check_timer)
                                }
                                return true;
                            } else {
                                $("span[id='fb_import_ok']").hide();
                                return false;
                            }
                        });
                }, 30000);
            }
        }
    });

});
