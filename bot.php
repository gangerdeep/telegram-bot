<?php

// ================= CONFIG =================
$TOKEN = "8525855467:AAEgyjEhpB75XMvwmSfXa-HJY-BeeFL1Rag";
$ADMIN_ID = 6415960307;

// ================= FILES =================
$user_map_file  = __DIR__ . "/user_map.json";
$all_users_file = __DIR__ . "/all_users.json";

$USER_MAP  = file_exists($user_map_file)  ? json_decode(file_get_contents($user_map_file), true)  : [];
$ALL_USERS = file_exists($all_users_file) ? json_decode(file_get_contents($all_users_file), true) : [];

// ================= GET UPDATE =================
$update = json_decode(file_get_contents("php://input"), true);
if (!isset($update["message"])) exit;

$msg     = $update["message"];
$chat_id = $msg["chat"]["id"];
$user_id = $msg["from"]["id"];
$text    = trim($msg["text"] ?? "");

// ================= SAVE / UPDATE USER =================
if ($user_id != $ADMIN_ID) {

    $ALL_USERS[$user_id] = [
        "name"     => $msg["from"]["first_name"] ?? "Unknown",
        "username" => isset($msg["from"]["username"])
            ? "@".$msg["from"]["username"]
            : "Not set"
    ];

    file_put_contents($all_users_file, json_encode($ALL_USERS, JSON_PRETTY_PRINT));
}

/* ================= ADMIN ================= */
if ($user_id == $ADMIN_ID) {

    // /start
    if ($text === "/start") {
        sendMessage($chat_id, "✅ Bot Running");
        exit;
    }

    // ================= /list =================
    if ($text === "/list") {

        if (!$ALL_USERS) {
            sendMessage($chat_id, "❌ No users yet");
            exit;
        }

        $list  = "📊 USER LIST\n";
        $list .= "↩️ Reply on this message to BROADCAST\n\n";

        foreach ($ALL_USERS as $uid => $u) {
            $list .=
                "👤 Name: {$u['name']}\n".
                "🔤 Username: {$u['username']}\n".
                "🆔 ID: $uid\n\n";
        }

        $sent = sendMessage($chat_id, $list);

        if (isset($sent["result"]["message_id"])) {
            $USER_MAP[$sent["result"]["message_id"]] = "BROADCAST";
            file_put_contents($user_map_file, json_encode($USER_MAP, JSON_PRETTY_PRINT));
        }
        exit;
    }

    // ================= /ad =================
    if ($text === "/ad") {

        if (!$ALL_USERS) {
            sendMessage($chat_id, "❌ No users to send ads");
            exit;
        }

        $photo_url = "https://i.ibb.co/rKCYcTGN/x.jpg";

        $caption =
      "📱 App Name – Duolingo\n\n".
      "#️⃣ [Ad] Learn a new language with the world's most-downloaded education app!             Duolingo is the fun, free app for learning 40+ languages through quick, bite-sized lessons";

        $keyboard = [
            "inline_keyboard" => [
                [
                    [
                        "text" => "Download Now 🔥",
                        "url"  => "https://play.google.com/store/apps/details?id=com.duolingo"
                    ]
                ]
            ]
        ];

        // ✅ SEND AD TO ADMIN
        api("sendPhoto", [
            "chat_id" => $ADMIN_ID,
            "photo" => $photo_url,
            "caption" => $caption,
            "reply_markup" => json_encode($keyboard)
        ]);

        // ✅ SEND AD TO ALL USERS
        foreach ($ALL_USERS as $uid => $u) {
            api("sendPhoto", [
                "chat_id" => $uid,
                "photo" => $photo_url,
                "caption" => $caption,
                "reply_markup" => json_encode($keyboard)
            ]);
        }

        sendMessage($chat_id, "✅ Ad sent to all users + admin");
        exit;
    }

    // ================= ADMIN REPLY =================
    if (isset($msg["reply_to_message"])) {

        $rid = $msg["reply_to_message"]["message_id"];
        $target = $USER_MAP[$rid] ?? null;

        // BROADCAST
        if ($target === "BROADCAST") {
            foreach ($ALL_USERS as $uid => $u) {
                isset($msg["text"])
                    ? sendMessage($uid, $msg["text"])
                    : copyMessage($uid, $chat_id, $msg["message_id"]);
            }
            exit;
        }

        // SINGLE USER
        if ($target) {
            isset($msg["text"])
                ? sendMessage($target, $msg["text"])
                : copyMessage($target, $chat_id, $msg["message_id"]);
            exit;
        }
    }

    exit;
}

/* ================= USER ================= */

// /start USER
if ($text === "/start") {

    sendMessage($chat_id, "👋 Hello {$ALL_USERS[$user_id]['name']}!");

    $note =
        "👤 New User Started Bot\n\n".
        "Name: {$ALL_USERS[$user_id]['name']}\n".
        "Username: {$ALL_USERS[$user_id]['username']}\n".
        "User ID: $user_id";

    $sent = sendMessage($ADMIN_ID, $note);

    if (isset($sent["result"]["message_id"])) {
        $USER_MAP[$sent["result"]["message_id"]] = $user_id;
        file_put_contents($user_map_file, json_encode($USER_MAP, JSON_PRETTY_PRINT));
    }
    exit;
}

// USER MESSAGE → ADMIN
$fwd = forwardMessage($ADMIN_ID, $chat_id, $msg["message_id"]);
if (isset($fwd["result"]["message_id"])) {
    $USER_MAP[$fwd["result"]["message_id"]] = $user_id;
    file_put_contents($user_map_file, json_encode($USER_MAP, JSON_PRETTY_PRINT));
}

/* ================= FUNCTIONS ================= */

function sendMessage($chat, $text) {
    return api("sendMessage", [
        "chat_id" => $chat,
        "text" => $text
    ]);
}

function forwardMessage($to, $from, $mid) {
    return api("forwardMessage", [
        "chat_id" => $to,
        "from_chat_id" => $from,
        "message_id" => $mid
    ]);
}

function copyMessage($to, $from, $mid) {
    return api("copyMessage", [
        "chat_id" => $to,
        "from_chat_id" => $from,
        "message_id" => $mid
    ]);
}

function api($method, $data) {
    global $TOKEN;

    $url = "https://api.telegram.org/bot$TOKEN/$method";

    $opts = [
        "http" => [
            "method" => "POST",
            "header" => "Content-Type: application/x-www-form-urlencoded",
            "content" => http_build_query($data)
        ]
    ];

    return json_decode(file_get_contents($url, false, stream_context_create($opts)), true);
}
