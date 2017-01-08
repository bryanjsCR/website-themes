odoo.define('mail_attachment_preview.chat_manager', function (require) {
"use strict";

var session = require('web.session');
var time = require('web.time');
var chat_manager = require('mail.chat_manager');

function parse_and_transform(html_string, transform_function) {
    var open_token = "OPEN" + Date.now();
    var string = html_string.replace(/&lt;/g, open_token);
    var children = $('<div>').html(string).contents();
    return _parse_and_transform(children, transform_function)
                .replace(new RegExp(open_token, "g"), "&lt;");
}

function _parse_and_transform(nodes, transform_function) {
    return _.map(nodes, function (node) {
        return transform_function(node, function () {
            return _parse_and_transform(node.childNodes, transform_function);
        });
    }).join("");
}
var url_regexp = /\b((?:https?:\/\/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gi;
function add_link (node, transform_children) {
    if (node.nodeType === 3) {  // text node
        return node.data.replace(url_regexp, function (url) {
            var href = (!/^(f|ht)tps?:\/\//i.test(url)) ? "http://" + url : url;
            return '<a target="_blank" href="' + href + '">' + url + '</a>';
        });
    }
    if (node.tagName === "A") return node.outerHTML;
    node.innerHTML = transform_children();
    return node.outerHTML;
}
var emoji_substitutions = {};
var emojis = [];

chat_manager.make_message = function (data) {
    var msg = {
        id: data.id,
        author_id: data.author_id,
        body_short: data.body_short || "",
        body: data.body || "",
        date: moment(time.str_to_datetime(data.date)),
        message_type: data.message_type,
        subtype_description: data.subtype_description,
        is_author: data.author_id && data.author_id[0] === session.partner_id,
        is_note: data.is_note,
        is_system_notification: data.message_type === 'notification' && data.model === 'mail.channel',
        attachment_ids: data.attachment_ids,
        subject: data.subject,
        email_from: data.email_from,
        record_name: data.record_name,
        tracking_value_ids: data.tracking_value_ids,
        channel_ids: data.channel_ids,
        model: data.model,
        res_id: data.res_id,
        url: session.url("/mail/view?message_id=" + data.id),
    };

    _.each(_.keys(emoji_substitutions), function (key) {
        var escaped_key = String(key).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
        var regexp = new RegExp("(?:^|\\s|<[a-z]*>)(" + escaped_key + ")(?=\\s|$|</[a-z]*>)", "g");
        msg.body = msg.body.replace(regexp, ' <span class="o_mail_emoji">'+emoji_substitutions[key]+'</span> ');
    });

    function property_descr(channel) {
        return {
            enumerable: true,
            get: function () {
                return _.contains(msg.channel_ids, channel);
            },
            set: function (bool) {
                if (bool) {
                    add_channel_to_message(msg, channel);
                } else {
                    msg.channel_ids = _.without(msg.channel_ids, channel);
                }
            }
        };
    }

    Object.defineProperties(msg, {
        is_starred: property_descr("channel_starred"),
        is_needaction: property_descr("channel_inbox"),
    });

    if (_.contains(data.needaction_partner_ids, session.partner_id)) {
        msg.is_needaction = true;
    }
    if (_.contains(data.starred_partner_ids, session.partner_id)) {
        msg.is_starred = true;
    }
    if (msg.model === 'mail.channel') {
        var real_channels = _.without(msg.channel_ids, 'channel_inbox', 'channel_starred');
        var origin = real_channels.length === 1 ? real_channels[0] : undefined;
        var channel = origin && chat_manager.get_channel(origin);
        if (channel) {
            msg.origin_id = origin;
            msg.origin_name = channel.name;
        }
    }

    // Compute displayed author name or email
    if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
        msg.mailto = msg.email_from;
    } else {
        msg.displayed_author = msg.author_id && msg.author_id[1] ||
                               msg.email_from || _t('Anonymous');
    }

    // Don't redirect on author clicked of self-posted messages
    msg.author_redirect = !msg.is_author;

    // Compute the avatar_url
    if (msg.author_id && msg.author_id[0]) {
        msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
    } else if (msg.message_type === 'email') {
        msg.avatar_src = "/mail/static/src/img/email_icon.png";
    } else {
        msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
    }

    // add anchor tags to urls
    msg.body = parse_and_transform(msg.body, add_link);

    // Compute url of attachments
    _.each(msg.attachment_ids, function(a) {
        a.url = '/web/content/' + a.id; // + '?download=true';
    });

    // format date to the local only once by message
    // can not be done in preprocess, since it alter the original value
    if (msg.tracking_value_ids && msg.tracking_value_ids.length) {
        _.each(msg.tracking_value_ids, function(f) {
            if (_.contains(['date', 'datetime'], f.field_type)) {
                var format = (f.field_type === 'date') ? 'LL' : 'LLL';
                if (f.old_value) {
                    f.old_value = moment.utc(f.old_value).local().format(format);
                }
                if (f.new_value) {
                    f.new_value = moment.utc(f.new_value).local().format(format);
                }
            }
        });
    }

    return msg;
};

function init () {
    var load_emojis = session.rpc("/mail/chat_init").then(function (result) {
       emojis = result.emoji;
       _.each(emojis, function(emoji) {
           emoji_substitutions[_.escape(emoji.source)] = emoji.substitution;
       });
   });
}

init();
});
