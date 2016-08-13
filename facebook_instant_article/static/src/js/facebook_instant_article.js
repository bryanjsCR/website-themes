odoo.define('facebook_instant_article.facebook_instant_article', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        var $fb_import_id = $("input[name='fb_import_id']");
        if (typeof $fb_import_id === 'undefined'){
            return;
        }
        if (typeof $fb_import_id.val() === 'undefined'){
            return;
        }
        if($fb_import_id.val() !== ""){
            console.log("import id");
            console.log($fb_import_id.val());
            //check import status
            ajax.jsonRpc('/fb_instant_article/check_import', 'call', {'fb_import_id': $fb_import_id.val()})
                .then(function(data){
                    console.log(data);
                });
        }
        else{
            console.log("no import id!");
        }
    });

});
