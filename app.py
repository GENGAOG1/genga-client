from flask import (
    Flask,
    send_file,
    render_template_string,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

import os
import uuid
import requests
import time
from functools import wraps


# ============================================================
# GENGA CLIENT - FLASK WEBSITE
# ============================================================

app = Flask(__name__)

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

app.secret_key = os.environ.get(
    "GENGA_SECRET_KEY",
    "change-this-secret-key"
)

DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    ""
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    ""
)

VALID_KEYS = [
    key.strip()
    for key in os.environ.get(
        "GENGA_VALID_KEYS",
        ""
    ).split(",")
    if key.strip()
]

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

# Kann jetzt direkt in Render geändert werden.
# Environment Variable:
# DISCORD_URL=https://discord.gg/DEINNEUERINVITE
DISCORD_URL = os.environ.get(
    "DISCORD_URL",
    "https://discord.gg/sw7zNs9T58"
)

ADMIN_URL = "https://genga-client.onrender.com/admin"


# Requests bleiben solange im RAM,
# wie die Render-Instanz läuft.
PENDING_REQUESTS = {}


# ============================================================
# HELPERS
# ============================================================

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(
                url_for("admin")
            )

        return func(*args, **kwargs)

    return wrapper


def cleanup_requests():
    """
    Löscht alte Download-Anfragen nach 24 Stunden.
    """

    now = time.time()
    max_age = 60 * 60 * 24

    expired = []

    for request_id, data in PENDING_REQUESTS.items():

        created = data.get(
            "created",
            now
        )

        if now - created > max_age:
            expired.append(request_id)

    for request_id in expired:

        PENDING_REQUESTS.pop(
            request_id,
            None
        )


def send_discord_notification(key, request_id):
    """
    Sendet eine neue Download-Anfrage an Discord.
    """

    if not DISCORD_WEBHOOK_URL:

        print(
            "DISCORD_WEBHOOK_URL ist nicht gesetzt."
        )

        return False

    payload = {
        "embeds": [
            {
                "title": "GENGA CLIENT - DOWNLOAD REQUEST",

                "description": (
                    "Eine neue Download-Anfrage wurde erstellt."
                ),

                "color": 16728064,

                "fields": [
                    {
                        "name": "Key",
                        "value": f"`{key}`",
                        "inline": False
                    },
                    {
                        "name": "Request ID",
                        "value": f"`{request_id}`",
                        "inline": False
                    },
                    {
                        "name": "Admin Panel",
                        "value": ADMIN_URL,
                        "inline": False
                    }
                ],

                "footer": {
                    "text": "GENGA Client"
                }
            }
        ]
    }

    try:

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        print(
            "Discord Webhook Status:",
            response.status_code
        )

        if response.status_code >= 400:

            print(
                "Discord Webhook Error:",
                response.text
            )

        return response.ok

    except Exception as error:

        print(
            "Discord Webhook Exception:",
            error
        )

        return False


# ============================================================
# MAIN WEBSITE
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GENGA Client</title>


    <style>

        * {
            box-sizing: border-box;
        }


        html {
            scroll-behavior: smooth;
        }


        body {

            margin: 0;

            min-height: 100vh;

            background: #090909;

            color: #e8e8e8;

            font-family:
                Arial,
                Helvetica,
                sans-serif;

            font-size: 14px;
        }


        a {
            color: inherit;
            text-decoration: none;
        }


        button,
        input {
            font: inherit;
        }


        /* ====================================================
           MAIN WRAPPER
           ==================================================== */

        .site {

            width: min(
                1050px,
                calc(100% - 28px)
            );

            margin: 35px auto 60px;

            border: 1px solid #252525;

            background: #0d0d0d;
        }


        /* ====================================================
           TOP BAR
           ==================================================== */

        .topbar {

            min-height: 58px;

            display: flex;

            align-items: center;

            justify-content: space-between;

            border-bottom: 1px solid #252525;

            padding: 0 18px;
        }


        .logo {

            display: flex;

            align-items: center;

            gap: 9px;

            font-size: 15px;

            font-weight: bold;

            letter-spacing: 0.08em;
        }


        .logo-mark {

            width: 5px;

            height: 20px;

            background: #f04b1c;
        }


        .version {

            color: #666;

            font-family:
                "Courier New",
                monospace;

            font-size: 11px;
        }


        .navigation {

            display: flex;

            align-items: center;

            gap: 2px;
        }


        .navigation a {

            padding: 9px 11px;

            color: #777;

            font-size: 10px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;
        }


        .navigation a:hover {

            color: #eee;

            background: #151515;
        }


        /* ====================================================
           CONTENT
           ==================================================== */

        .content {

            padding: 22px;
        }


        /* ====================================================
           SMALL PAGE TITLE
           ==================================================== */

        .title {

            padding: 4px 0 22px;

            border-bottom: 1px solid #202020;

            margin-bottom: 14px;
        }


        .title h1 {

            margin: 0;

            font-size: 25px;

            font-weight: bold;

            letter-spacing: -0.02em;
        }


        .title p {

            margin: 7px 0 0;

            color: #707070;

            font-size: 12px;
        }


        /* ====================================================
           ALERT
           ==================================================== */

        .alert {

            margin-bottom: 14px;

            padding: 11px 13px;

            border-left: 3px solid #f04b1c;

            background: #141414;

            color: #aaa;

            font-size: 12px;
        }


        /* ====================================================
           MAIN TWO COLUMNS
           ==================================================== */

        .main-grid {

            display: grid;

            grid-template-columns: 1fr 1fr;

            gap: 14px;
        }


        .box {

            min-width: 0;

            background: #101010;

            border: 1px solid #292929;
        }


        .box-header {

            min-height: 43px;

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 0 14px;

            border-bottom: 1px solid #252525;

            background: #111111;
        }


        .box-header strong {

            font-size: 11px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;
        }


        .box-header span {

            color: #555;

            font-family:
                "Courier New",
                monospace;

            font-size: 10px;
        }


        .box-content {

            padding: 17px;
        }


        .box-content h2 {

            margin: 0 0 8px;

            font-size: 20px;
        }


        .box-content p {

            margin: 0;

            color: #707070;

            font-size: 12px;

            line-height: 1.6;
        }


        /* ====================================================
           DOWNLOAD
           ==================================================== */

        .download-file {

            margin-top: 20px;

            padding: 12px;

            border: 1px solid #242424;

            background: #0b0b0b;
        }


        .download-file small {

            display: block;

            margin-bottom: 5px;

            color: #555;

            font-size: 9px;

            text-transform: uppercase;

            letter-spacing: 0.1em;
        }


        .download-file code {

            color: #bbb;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;
        }


        .download-button {

            display: flex;

            align-items: center;

            justify-content: center;

            width: 100%;

            height: 43px;

            margin-top: 9px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: #fff;

            font-size: 11px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;
        }


        .download-button:hover {

            background: #ff5b27;

            border-color: #ff5b27;
        }


        .waiting-text {

            margin-top: 20px;

            padding: 12px;

            border: 1px solid #242424;

            color: #666;

            background: #0b0b0b;

            font-size: 11px;
        }


        /* ====================================================
           ACCESS
           ==================================================== */

        .key-form {

            margin-top: 19px;
        }


        .key-label {

            display: block;

            margin-bottom: 7px;

            color: #666;

            font-size: 9px;

            font-weight: bold;

            letter-spacing: 0.1em;

            text-transform: uppercase;
        }


        .key-row {

            display: flex;

            gap: 7px;
        }


        .key-input {

            width: 100%;

            height: 43px;

            padding: 0 12px;

            border: 1px solid #303030;

            outline: none;

            background: #090909;

            color: #eee;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;
        }


        .key-input::placeholder {

            color: #4d4d4d;
        }


        .key-input:focus {

            border-color: #555;
        }


        .request-button {

            height: 43px;

            padding: 0 18px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: white;

            font-size: 10px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;
        }


        .request-button:hover {

            background: #ff5b27;

            border-color: #ff5b27;
        }


        /* ====================================================
           DISCORD
           ==================================================== */

        .discord {

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-top: 10px;

            padding: 12px;

            border: 1px solid #292929;

            background: #0b0b0b;

            color: #999;

            font-size: 11px;
        }


        .discord:hover {

            color: #eee;

            border-color: #414141;
        }


        .discord-right {

            color: #555;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;
        }


        /* ====================================================
           INFORMATION
           ==================================================== */

        .section {

            margin-top: 28px;
        }


        .section-title {

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-bottom: 8px;

            padding-bottom: 9px;

            border-bottom: 1px solid #252525;
        }


        .section-title strong {

            font-size: 12px;

            text-transform: uppercase;

            letter-spacing: 0.08em;
        }


        .section-title span {

            color: #4f4f4f;

            font-size: 10px;
        }


        .information {

            border: 1px solid #292929;

            background: #101010;
        }


        .info-row {

            display: grid;

            grid-template-columns: 150px 1fr;

            min-height: 43px;

            border-bottom: 1px solid #202020;
        }


        .info-row:last-child {

            border-bottom: 0;
        }


        .info-name {

            display: flex;

            align-items: center;

            padding: 0 13px;

            color: #5c5c5c;

            background: #0d0d0d;

            border-right: 1px solid #202020;

            font-size: 10px;

            font-weight: bold;

            text-transform: uppercase;

            letter-spacing: 0.07em;
        }


        .info-value {

            display: flex;

            align-items: center;

            padding: 0 13px;

            color: #bdbdbd;

            font-size: 12px;
        }


        /* ====================================================
           FOOTER
           ==================================================== */

        .footer {

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-top: 28px;

            padding-top: 15px;

            border-top: 1px solid #202020;

            color: #4c4c4c;

            font-size: 10px;
        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 700px) {

            .site {

                width: calc(100% - 16px);

                margin-top: 8px;
            }


            .topbar {

                padding: 0 12px;
            }


            .navigation {

                display: none;
            }


            .content {

                padding: 12px;
            }


            .main-grid {

                grid-template-columns: 1fr;
            }


            .key-row {

                flex-direction: column;
            }


            .request-button {

                width: 100%;
            }


            .info-row {

                grid-template-columns: 110px 1fr;
            }


            .footer {

                flex-direction: column;

                align-items: flex-start;

                gap: 6px;
            }
        }

    </style>

</head>


<body>


<div class="site">


    <!-- ====================================================
         TOP BAR
         ==================================================== -->

    <header class="topbar">

        <a href="/" class="logo">

            <span class="logo-mark"></span>

            GENGA CLIENT

        </a>


        <nav class="navigation">

            <a href="#download">
                Download
            </a>

            <a href="#access">
                Access
            </a>

            <a href="#information">
                Info
            </a>

            <a
                href="{{ discord_url }}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Discord
            </a>

        </nav>


        <div class="version">
            1.21.11
        </div>

    </header>


    <!-- ====================================================
         CONTENT
         ==================================================== -->

    <main class="content">


        <!-- TITLE -->

        <div class="title">

            <h1>
                GENGA Client
            </h1>

            <p>
                Minecraft 1.21.11
            </p>

        </div>


        <!-- ERROR MESSAGE -->

        {% if message %}

            <div class="alert">
                {{ message }}
            </div>

        {% endif %}


        <!-- =================================================
             DOWNLOAD + ACCESS
             ================================================= -->

        <section class="main-grid">


            <!-- DOWNLOAD -->

            <div
                class="box"
                id="download"
            >

                <div class="box-header">

                    <strong>
                        Download
                    </strong>

                    <span>
                        CLIENT
                    </span>

                </div>


                <div class="box-content">

                    <h2>
                        GENGA Client
                    </h2>

                    <p>
                        Download the current GENGA Client
                        build for Minecraft 1.21.11.
                    </p>


                    <div class="download-file">

                        <small>
                            File
                        </small>

                        <code>
                            {{ download_datei }}
                        </code>

                    </div>


                    {% if download_ready %}

                        <a
                            class="download-button"
                            href="{{ url_for(
                                'download',
                                request_id=request_id
                            ) }}"
                        >
                            Download
                        </a>

                    {% else %}

                        <div class="waiting-text">
                            Enter your access key and request access
                            to the download.
                        </div>

                    {% endif %}

                </div>

            </div>


            <!-- ACCESS -->

            <div
                class="box"
                id="access"
            >

                <div class="box-header">

                    <strong>
                        Access
                    </strong>

                    <span>
                        KEY
                    </span>

                </div>


                <div class="box-content">

                    <h2>
                        Access Key
                    </h2>

                    <p>
                        Enter your GENGA access key below.
                        Your request will be sent for approval.
                    </p>


                    {% if not download_ready %}

                        <form
                            class="key-form"
                            method="POST"
                            action="{{ url_for(
                                'request_download'
                            ) }}"
                        >

                            <label
                                class="key-label"
                                for="key"
                            >
                                Access Key
                            </label>


                            <div class="key-row">

                                <input
                                    class="key-input"
                                    id="key"
                                    type="text"
                                    name="key"
                                    placeholder="GENGA-XXXX-XXXX"
                                    autocomplete="off"
                                    required
                                >


                                <button
                                    class="request-button"
                                    type="submit"
                                >
                                    Request
                                </button>

                            </div>

                        </form>

                    {% else %}

                        <div class="waiting-text">
                            Access has been approved.
                            The download is available on the left.
                        </div>

                    {% endif %}


                    <a
                        class="discord"
                        href="{{ discord_url }}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >

                        <span>
                            Join GENGA Discord
                        </span>

                        <span class="discord-right">
                            →
                        </span>

                    </a>

                </div>

            </div>

        </section>


        <!-- =================================================
             INFORMATION
             ================================================= -->

        <section
            class="section"
            id="information"
        >

            <div class="section-title">

                <strong>
                    Information
                </strong>

                <span>
                    GENGA CLIENT
                </span>

            </div>


            <div class="information">


                <div class="info-row">

                    <div class="info-name">
                        Client
                    </div>

                    <div class="info-value">
                        GENGA Client
                    </div>

                </div>


                <div class="info-row">

                    <div class="info-name">
                        Minecraft
                    </div>

                    <div class="info-value">
                        1.21.11
                    </div>

                </div>


                <div class="info-row">

                    <div class="info-name">
                        Loader
                    </div>

                    <div class="info-value">
                        Fabric
                    </div>

                </div>


                <div class="info-row">

                    <div class="info-name">
                        Version
                    </div>

                    <div class="info-value">
                        1.0.0
                    </div>

                </div>


                <div class="info-row">

                    <div class="info-name">
                        Access
                    </div>

                    <div class="info-value">
                        Access Key required
                    </div>

                </div>


            </div>

        </section>


        <!-- =================================================
             FOOTER
             ================================================= -->

        <footer class="footer">

            <span>
                GENGA Client
            </span>

            <span>
                Minecraft 1.21.11
            </span>

        </footer>


    </main>

</div>


<!-- ========================================================
     APPROVAL SCRIPT
     ======================================================== -->

<script>

    const requestId =
        {{ request_id|tojson }};

    const approvalView =
        {{ approval_view|tojson }};


    let approvalHandled = false;


    async function checkStatus() {

        if (!requestId) {
            return;
        }


        if (approvalView) {
            return;
        }


        if (approvalHandled) {
            return;
        }


        try {

            const response = await fetch(
                "/status/" +
                encodeURIComponent(requestId),
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


            if (!response.ok) {

                scheduleNextCheck();

                return;
            }


            const data =
                await response.json();


            if (data.status === "approved") {

                /*
                 * Nur EINMAL weiterleiten.
                 */

                approvalHandled = true;


                window.location.replace(
                    "/?request=" +
                    encodeURIComponent(requestId) +
                    "&approved=1"
                );


                return;
            }


            scheduleNextCheck();

        }

        catch (error) {

            console.log(
                "Approval check failed:",
                error
            );

            scheduleNextCheck();
        }

    }


    function scheduleNextCheck() {

        if (approvalHandled) {
            return;
        }


        if (approvalView) {
            return;
        }


        setTimeout(
            checkStatus,
            2000
        );

    }


    /*
     * Nur während die Anfrage noch nicht
     * freigegeben wurde.
     */

    if (
        requestId &&
        !approvalView
    ) {

        checkStatus();

    }

</script>


</body>

</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def index():

    cleanup_requests()

    request_id = request.args.get(
        "request"
    )

    message = None


    if request.args.get("error") == "invalid":

        message = (
            "The entered access key is invalid."
        )


    elif request.args.get("error") == "missing":

        message = (
            "Please enter an access key."
        )


    elif request.args.get("error") == "expired":

        message = (
            "This download request no longer exists."
        )


    elif request.args.get("error") == "notapproved":

        message = (
            "Your request has not been approved yet."
        )


    download_ready = False


    if request_id:

        request_data = PENDING_REQUESTS.get(
            request_id
        )


        if request_data:

            if request_data.get(
                "approved"
            ) is True:

                download_ready = True


    approval_view = (
        request.args.get("approved") == "1"
        and download_ready
    )


    return render_template_string(

        HTML,

        request_id=request_id,

        download_ready=download_ready,

        approval_view=approval_view,

        discord_url=DISCORD_URL,

        download_datei=DOWNLOAD_DATEI,

        message=message
    )


# ============================================================
# REQUEST DOWNLOAD
# ============================================================

@app.route(
    "/request-download",
    methods=["POST"]
)
def request_download():

    cleanup_requests()

    key = request.form.get(
        "key",
        ""
    ).strip()


    if not key:

        return redirect(
            url_for(
                "index",
                error="missing"
            )
        )


    if key not in VALID_KEYS:

        return redirect(
            url_for(
                "index",
                error="invalid"
            )
        )


    request_id = str(
        uuid.uuid4()
    )


    PENDING_REQUESTS[request_id] = {

        "key": key,

        "approved": False,

        "created": time.time()

    }


    webhook_success = (
        send_discord_notification(
            key,
            request_id
        )
    )


    if not webhook_success:

        print(
            "WARNUNG: Discord-Benachrichtigung "
            "konnte nicht gesendet werden."
        )


    return redirect(
        url_for(
            "index",
            request=request_id
        )
    )


# ============================================================
# STATUS
# ============================================================

@app.route(
    "/status/<request_id>",
    methods=["GET"]
)
def status(request_id):

    request_data = PENDING_REQUESTS.get(
        request_id
    )


    if not request_data:

        return jsonify({
            "status": "not_found"
        }), 404


    if request_data.get(
        "approved"
    ) is True:

        return jsonify({
            "status": "approved"
        })


    return jsonify({
        "status": "pending"
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

ADMIN_LOGIN_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GENGA Admin</title>


    <style>

        * {
            box-sizing: border-box;
        }


        body {

            margin: 0;

            min-height: 100vh;

            display: flex;

            align-items: center;

            justify-content: center;

            background: #090909;

            color: #eee;

            font-family:
                Arial,
                Helvetica,
                sans-serif;
        }


        .login {

            width: min(
                390px,
                calc(100% - 24px)
            );

            border: 1px solid #292929;

            background: #101010;
        }


        .header {

            padding: 15px;

            border-bottom: 1px solid #252525;

            font-size: 11px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;
        }


        .header span {

            color: #f04b1c;
        }


        .content {

            padding: 18px;
        }


        h1 {

            margin: 0 0 7px;

            font-size: 22px;
        }


        p {

            margin: 0;

            color: #666;

            font-size: 12px;
        }


        input {

            width: 100%;

            height: 43px;

            margin-top: 18px;

            padding: 0 12px;

            background: #090909;

            border: 1px solid #303030;

            outline: none;

            color: white;
        }


        input:focus {

            border-color: #555;
        }


        button {

            width: 100%;

            height: 43px;

            margin-top: 8px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: white;

            font-size: 10px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;
        }


        button:hover {

            background: #ff5b27;
        }


        .error {

            margin-top: 12px;

            color: #ff6868;

            font-size: 11px;
        }

    </style>

</head>


<body>


<div class="login">


    <div class="header">

        <span>GENGA</span>
        / ADMIN

    </div>


    <div class="content">

        <h1>
            Admin Panel
        </h1>


        <p>
            Manage download requests.
        </p>


        <form method="POST">

            <input
                type="password"
                name="password"
                placeholder="Admin password"
                autocomplete="current-password"
                required
            >


            <button type="submit">
                Login
            </button>

        </form>


        {% if error %}

            <div class="error">
                {{ error }}
            </div>

        {% endif %}

    </div>

</div>


</body>

</html>
"""


@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if password == ADMIN_PASSWORD:

            session[
                "admin_logged_in"
            ] = True


            return redirect(
                url_for("admin_panel")
            )


        return render_template_string(
            ADMIN_LOGIN_HTML,
            error="Invalid password."
        )


    if session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_panel")
        )


    return render_template_string(
        ADMIN_LOGIN_HTML,
        error=None
    )


# ============================================================
# ADMIN PANEL
# ============================================================

@app.route(
    "/admin/panel",
    methods=["GET"]
)
@admin_required
def admin_panel():

    cleanup_requests()

    requests_list = []


    for request_id, data in (
        PENDING_REQUESTS.items()
    ):

        requests_list.append({

            "id": request_id,

            "key": data.get(
                "key",
                ""
            ),

            "approved": data.get(
                "approved",
                False
            ),

            "created": data.get(
                "created",
                0
            )

        })


    requests_list.sort(
        key=lambda item: item["created"],
        reverse=True
    )


    rows = ""


    for item in requests_list:

        created_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                item["created"]
            )
        )


        if item["approved"]:

            status_html = """
                <span class="approved">
                    APPROVED
                </span>
            """

            action_html = """
                <span class="done">
                    ACCESS GRANTED
                </span>
            """

        else:

            status_html = """
                <span class="pending">
                    PENDING
                </span>
            """

            action_html = f"""
                <form
                    method="POST"
                    action="/admin/approve/{item['id']}"
                >

                    <button class="approve">
                        APPROVE
                    </button>

                </form>
            """


        rows += f"""
            <tr>

                <td>
                    <code>{item['id']}</code>
                </td>

                <td>
                    <code>{item['key']}</code>
                </td>

                <td>
                    {status_html}
                </td>

                <td>
                    {created_time}
                </td>

                <td>
                    {action_html}
                </td>

            </tr>
        """


    if not rows:

        rows = """
            <tr>

                <td
                    colspan="5"
                    class="empty"
                >
                    No download requests yet.
                </td>

            </tr>
        """


    admin_html = f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GENGA Admin</title>


    <style>

        * {{
            box-sizing: border-box;
        }}


        body {{

            margin: 0;

            min-height: 100vh;

            background: #090909;

            color: #eee;

            font-family:
                Arial,
                Helvetica,
                sans-serif;
        }}


        .container {{

            width: min(
                1200px,
                calc(100% - 24px)
            );

            margin: 30px auto;
        }}


        .top {{

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding-bottom: 15px;

            border-bottom: 1px solid #252525;
        }}


        h1 {{

            margin: 0;

            font-size: 22px;
        }}


        .sub {{

            margin-top: 5px;

            color: #666;

            font-size: 11px;
        }}


        .logout {{

            padding: 9px 12px;

            border: 1px solid #292929;

            color: #777;

            font-size: 10px;

            text-transform: uppercase;
        }}


        .logout:hover {{

            color: #eee;

            border-color: #444;
        }}


        .table-wrap {{

            margin-top: 14px;

            overflow-x: auto;

            border: 1px solid #292929;
        }}


        table {{

            width: 100%;

            min-width: 850px;

            border-collapse: collapse;
        }}


        th {{

            padding: 12px;

            text-align: left;

            background: #111;

            color: #555;

            font-size: 9px;

            text-transform: uppercase;

            letter-spacing: 0.08em;
        }}


        td {{

            padding: 12px;

            border-top: 1px solid #202020;

            background: #0e0e0e;

            font-size: 11px;
        }}


        code {{

            color: #aaa;

            font-family:
                "Courier New",
                monospace;

            font-size: 10px;
        }}


        .approved {{

            color: #50c98a;

            font-weight: bold;

            font-size: 10px;
        }}


        .pending {{

            color: #f06a3a;

            font-weight: bold;

            font-size: 10px;
        }}


        .done {{

            color: #555;

            font-size: 9px;

            font-weight: bold;
        }}


        .approve {{

            padding: 8px 12px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: white;

            font-size: 9px;

            font-weight: bold;

            cursor: pointer;
        }}


        .approve:hover {{

            background: #ff5b27;
        }}


        .empty {{

            padding: 35px;

            text-align: center;

            color: #555;
        }}

    </style>

</head>


<body>


<div class="container">


    <div class="top">

        <div>

            <h1>
                GENGA Admin
            </h1>

            <div class="sub">
                Download requests
            </div>

        </div>


        <a
            class="logout"
            href="/admin/logout"
        >
            Logout
        </a>

    </div>


    <div class="table-wrap">

        <table>

            <thead>

                <tr>

                    <th>
                        Request ID
                    </th>

                    <th>
                        Key
                    </th>

                    <th>
                        Status
                    </th>

                    <th>
                        Created
                    </th>

                    <th>
                        Action
                    </th>

                </tr>

            </thead>


            <tbody>

                {rows}

            </tbody>

        </table>

    </div>


</div>


</body>

</html>
"""


    return admin_html


# ============================================================
# APPROVE REQUEST
# ============================================================

@app.route(
    "/admin/approve/<request_id>",
    methods=["POST"]
)
@admin_required
def approve_request(request_id):

    request_data = PENDING_REQUESTS.get(
        request_id
    )


    if request_data:

        request_data[
            "approved"
        ] = True


        print(
            "Approved request:",
            request_id
        )


    return redirect(
        url_for("admin_panel")
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin")
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route(
    "/download/<request_id>",
    methods=["GET"]
)
def download(request_id):

    request_data = PENDING_REQUESTS.get(
        request_id
    )


    if not request_data:

        return redirect(
            url_for(
                "index",
                error="expired"
            )
        )


    if request_data.get(
        "approved"
    ) is not True:

        return redirect(
            url_for(
                "index",
                request=request_id,
                error="notapproved"
            )
        )


    file_path = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        DOWNLOAD_DATEI
    )


    if not os.path.isfile(
        file_path
    ):

        return (
            "Download file not found on server.",
            404
        )


    return send_file(

        file_path,

        as_attachment=True,

        download_name=DOWNLOAD_DATEI
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "service": "GENGA Client"

    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port
    )
