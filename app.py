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


# ============================================================
# CONFIG
# ============================================================

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


# ------------------------------------------------------------
# GENGA DOWNLOAD
# ------------------------------------------------------------

DOWNLOAD_DATEI = "GENGA-Client.jar"

SOURCE_DATEI = "WaterClientDevVersionByDexter_PRIVACY_CLEAN.jar"


# ------------------------------------------------------------
# DISCORD
# ------------------------------------------------------------

DISCORD_URL = "https://discord.gg/sw7zNs9T58"


# ------------------------------------------------------------
# ADMIN
# ------------------------------------------------------------

ADMIN_URL = "https://genga-client.onrender.com/admin"


# ------------------------------------------------------------
# REQUEST STORAGE
# ------------------------------------------------------------

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

    now = time.time()

    max_age = 60 * 60 * 24

    expired = []

    for request_id, data in PENDING_REQUESTS.items():

        created = data.get(
            "created",
            now
        )

        if now - created > max_age:

            expired.append(
                request_id
            )

    for request_id in expired:

        PENDING_REQUESTS.pop(
            request_id,
            None
        )


def send_discord_notification(
    key,
    request_id
):

    if not DISCORD_WEBHOOK_URL:

        print(
            "DISCORD_WEBHOOK_URL ist nicht gesetzt."
        )

        return False


    payload = {

        "embeds": [

            {

                "title":
                    "GENGA CLIENT - DOWNLOAD REQUEST",

                "description":
                    "Eine neue Download-Anfrage wurde erstellt.",

                "color":
                    39423,

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

            background:
                radial-gradient(
                    circle at 50% -10%,
                    rgba(0, 174, 255, 0.18),
                    transparent 38%
                ),
                radial-gradient(
                    circle at 100% 100%,
                    rgba(0, 91, 255, 0.10),
                    transparent 35%
                ),
                #050911;

            color: #e9f7ff;

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
           PAGE
           ==================================================== */

        .page {

            width: min(
                780px,
                calc(100% - 30px)
            );

            margin: 55px auto;

        }


        /* ====================================================
           HEADER
           ==================================================== */

        header {

            position: relative;

            padding: 28px 28px 25px;

            border: 1px solid rgba(70, 170, 255, 0.18);

            border-radius: 18px;

            margin-bottom: 28px;

            background:
                linear-gradient(
                    145deg,
                    rgba(12, 25, 43, 0.94),
                    rgba(5, 11, 21, 0.94)
                );

            box-shadow:
                0 0 40px rgba(0, 128, 255, 0.07),
                inset 0 1px rgba(255, 255, 255, 0.03);

            overflow: hidden;
        }


        header::before {

            content: "";

            position: absolute;

            left: 0;

            top: 0;

            width: 100%;

            height: 2px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    #29c8ff,
                    #3b7dff,
                    transparent
                );

            opacity: 0.9;
        }


        .brand {

            font-size: 27px;

            font-weight: 800;

            letter-spacing: 0.02em;

            color: #ffffff;

            text-shadow:
                0 0 22px rgba(39, 193, 255, 0.18);
        }


        .brand span {

            color: #27c9ff;

            text-shadow:
                0 0 18px rgba(39, 201, 255, 0.35);
        }


        .version {

            margin-top: 7px;

            color: #6f91aa;

            font-size: 12px;

            letter-spacing: 0.03em;
        }


        /* ====================================================
           SECTIONS
           ==================================================== */

        section {

            margin-bottom: 22px;

            padding: 24px;

            border: 1px solid rgba(70, 170, 255, 0.13);

            border-radius: 18px;

            background:
                linear-gradient(
                    145deg,
                    rgba(10, 21, 36, 0.88),
                    rgba(5, 11, 20, 0.90)
                );

            box-shadow:
                0 15px 45px rgba(0, 0, 0, 0.25);

            backdrop-filter: blur(12px);
        }


        h2 {

            margin: 0 0 14px;

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 0.14em;

            text-transform: uppercase;

            color: #36c9ff;
        }


        .line {

            height: 1px;

            border: 0;

            background:
                linear-gradient(
                    90deg,
                    rgba(42, 196, 255, 0.30),
                    rgba(42, 196, 255, 0.04),
                    transparent
                );

            margin-bottom: 20px;
        }


        /* ====================================================
           DOWNLOAD
           ==================================================== */

        .download-name {

            font-size: 21px;

            font-weight: 700;

            color: #f2fbff;
        }


        .download-description {

            margin-top: 8px;

            color: #70869a;

            line-height: 1.6;
        }


        .file {

            margin-top: 18px;

            padding: 13px 14px;

            border: 1px solid rgba(61, 169, 255, 0.18);

            border-radius: 10px;

            background:
                rgba(2, 9, 18, 0.85);

            color: #7fa9c2;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;

            overflow-x: auto;

            box-shadow:
                inset 0 0 18px rgba(0, 123, 255, 0.035);
        }


        .download-button {

            display: inline-flex;

            align-items: center;

            justify-content: center;

            min-width: 155px;

            height: 44px;

            margin-top: 14px;

            padding: 0 20px;

            border: 1px solid #24c7ff;

            border-radius: 10px;

            background:
                linear-gradient(
                    135deg,
                    #19bfff,
                    #257cff
                );

            color: #fff;

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            box-shadow:
                0 0 22px rgba(25, 176, 255, 0.18);

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease,
                filter 0.15s ease;
        }


        .download-button:hover {

            transform: translateY(-2px);

            filter: brightness(1.08);

            box-shadow:
                0 0 30px rgba(25, 176, 255, 0.32);
        }


        .download-waiting {

            margin-top: 16px;

            padding: 11px 13px;

            border: 1px solid rgba(66, 153, 214, 0.12);

            border-radius: 9px;

            background: rgba(3, 12, 22, 0.65);

            color: #668096;

            font-size: 12px;

            line-height: 1.6;
        }


        /* ====================================================
           ACCESS
           ==================================================== */

        .access-text {

            color: #71879a;

            line-height: 1.6;

            margin-bottom: 17px;
        }


        .key-row {

            display: flex;

            gap: 9px;

            max-width: 600px;
        }


        .key-input {

            flex: 1;

            min-width: 0;

            height: 44px;

            padding: 0 13px;

            background:
                rgba(2, 9, 18, 0.85);

            border: 1px solid #203b52;

            border-radius: 10px;

            outline: none;

            color: #e9f8ff;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;

            transition:
                border-color 0.15s ease,
                box-shadow 0.15s ease;
        }


        .key-input::placeholder {

            color: #40576a;
        }


        .key-input:focus {

            border-color: #27bfff;

            box-shadow:
                0 0 0 3px rgba(39, 191, 255, 0.08),
                0 0 20px rgba(39, 191, 255, 0.05);
        }


        .request-button {

            height: 44px;

            padding: 0 20px;

            background:
                linear-gradient(
                    135deg,
                    #16bfff,
                    #286eff
                );

            border: 1px solid #27c6ff;

            border-radius: 10px;

            color: #fff;

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;

            box-shadow:
                0 0 20px rgba(31, 164, 255, 0.13);

            transition:
                transform 0.15s ease,
                filter 0.15s ease,
                box-shadow 0.15s ease;
        }


        .request-button:hover {

            transform: translateY(-1px);

            filter: brightness(1.08);

            box-shadow:
                0 0 25px rgba(31, 164, 255, 0.25);
        }


        /* ====================================================
           DISCORD
           ==================================================== */

        .discord {

            margin-top: 22px;

            padding: 14px 15px;

            border: 1px solid rgba(82, 147, 255, 0.12);

            border-radius: 10px;

            background:
                rgba(4, 12, 24, 0.55);

            font-size: 12px;
        }


        .discord-label {

            color: #587084;

            margin-right: 6px;
        }


        .discord-link {

            color: #78b9db;

            font-family:
                "Courier New",
                monospace;

            transition: color 0.15s ease;
        }


        .discord-link:hover {

            color: #2bcaff;

            text-shadow:
                0 0 10px rgba(43, 202, 255, 0.3);
        }


        /* ====================================================
           MESSAGE
           ==================================================== */

        .message {

            margin-bottom: 22px;

            padding: 14px 16px;

            border: 1px solid rgba(41, 191, 255, 0.16);

            border-left: 3px solid #27c7ff;

            border-radius: 10px;

            background:
                rgba(7, 21, 35, 0.85);

            color: #91afc1;

            font-size: 12px;

            line-height: 1.5;

            box-shadow:
                0 0 20px rgba(0, 153, 255, 0.04);
        }


        /* ====================================================
           INFORMATION
           ==================================================== */

        .info {

            border-top: 1px solid rgba(64, 137, 189, 0.14);

            border-radius: 8px;

            overflow: hidden;
        }


        .info-row {

            display: flex;

            justify-content: space-between;

            gap: 20px;

            padding: 14px 13px;

            border-bottom: 1px solid rgba(48, 102, 139, 0.10);

            background:
                rgba(3, 10, 19, 0.38);
        }


        .info-row:last-child {

            border-bottom: 0;
        }


        .info-name {

            color: #547084;

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: 0.08em;
        }


        .info-value {

            color: #9cc2d7;

            text-align: right;

            font-size: 12px;
        }


        /* ====================================================
           FOOTER
           ==================================================== */

        footer {

            padding: 20px 5px;

            color: #3e5668;

            font-size: 11px;

            text-align: center;

            letter-spacing: 0.02em;
        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 600px) {

            .page {

                width: calc(100% - 18px);

                margin: 25px auto;
            }


            header {

                padding: 23px 20px;

                margin-bottom: 16px;

                border-radius: 15px;
            }


            .brand {

                font-size: 22px;
            }


            section {

                padding: 19px;

                border-radius: 15px;

            }


            .key-row {

                flex-direction: column;
            }


            .request-button {

                width: 100%;
            }


            .download-button {

                width: 100%;
            }


            .info-row {

                flex-direction: column;

                gap: 5px;
            }


            .info-value {

                text-align: left;
            }

        }

    </style>

</head>


<body>


<div class="page">


    <!-- ====================================================
         HEADER
         ==================================================== -->

    <header>

        <div class="brand">

            GENGA <span>CLIENT</span>

        </div>


        <div class="version">

            Minecraft 1.21.11

        </div>

    </header>


    <!-- ====================================================
         MESSAGE
         ==================================================== -->

    {% if message %}

        <div class="message">

            {{ message }}

        </div>

    {% endif %}


    <!-- ====================================================
         DOWNLOAD
         ==================================================== -->

    <section id="download">

        <h2>
            Download
        </h2>


        <div class="line"></div>


        <div class="download-name">

            GENGA Client

        </div>


        <div class="download-description">

            Current GENGA Client build for Minecraft 1.21.11.

        </div>


        <div class="file">

            {{ download_datei }}

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

            <div class="download-waiting">

                Request access below to unlock the download.

            </div>

        {% endif %}

    </section>


    <!-- ====================================================
         ACCESS
         ==================================================== -->

    <section id="access">

        <h2>
            Access
        </h2>


        <div class="line"></div>


        {% if not download_ready %}

            <div class="access-text">

                Enter your GENGA access key to request access.

            </div>


            <form
                method="POST"
                action="{{ url_for(
                    'request_download'
                ) }}"
            >

                <div class="key-row">

                    <input
                        class="key-input"
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

            <div class="access-text">

                Your access has been approved.
                The download is available above.

            </div>

        {% endif %}


        <div class="discord">

            <span class="discord-label">
                Discord:
            </span>

            <a
                class="discord-link"
                href="https://discord.gg/sw7zNs9T58"
                target="_blank"
                rel="noopener noreferrer"
            >

                https://discord.gg/sw7zNs9T58

            </a>

        </div>

    </section>


    <!-- ====================================================
         INFORMATION
         ==================================================== -->

    <section id="information">

        <h2>
            Information
        </h2>


        <div class="line"></div>


        <div class="info">


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


    <!-- ====================================================
         FOOTER
         ==================================================== -->

    <footer>

        GENGA Client · Minecraft 1.21.11

    </footer>


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

@app.route(
    "/",
    methods=["GET"]
)
def index():

    cleanup_requests()


    request_id = request.args.get(
        "request"
    )


    message = None


    if request.args.get(
        "error"
    ) == "invalid":

        message = (
            "The entered access key is invalid."
        )


    elif request.args.get(
        "error"
    ) == "missing":

        message = (
            "Please enter an access key."
        )


    elif request.args.get(
        "error"
    ) == "expired":

        message = (
            "This download request no longer exists."
        )


    elif request.args.get(
        "error"
    ) == "notapproved":

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

        request.args.get(
            "approved"
        ) == "1"

        and

        download_ready

    )


    return render_template_string(

        HTML,

        request_id=request_id,

        download_ready=download_ready,

        approval_view=approval_view,

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


    webhook_success = send_discord_notification(

        key,

        request_id

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
# APPROVAL CHECK
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

            background:
                radial-gradient(
                    circle at top,
                    rgba(0, 174, 255, 0.14),
                    transparent 40%
                ),
                #050911;

            color: #e9f7ff;

            font-family:
                Arial,
                Helvetica,
                sans-serif;
        }


        .login {

            width: min(
                400px,
                calc(100% - 24px)
            );

            padding: 28px;

            border: 1px solid rgba(70, 170, 255, 0.18);

            border-radius: 18px;

            background:
                linear-gradient(
                    145deg,
                    rgba(12, 25, 43, 0.96),
                    rgba(5, 11, 21, 0.96)
                );

            box-shadow:
                0 20px 70px rgba(0, 0, 0, 0.4),
                0 0 35px rgba(0, 128, 255, 0.06);

            position: relative;
        }


        .login::before {

            content: "";

            position: absolute;

            left: 0;

            top: 0;

            width: 100%;

            height: 2px;

            border-radius: 18px 18px 0 0;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    #29c8ff,
                    transparent
                );
        }


        h1 {

            margin: 0;

            font-size: 24px;

            color: #fff;
        }


        p {

            margin: 7px 0 20px;

            color: #668196;

            font-size: 12px;
        }


        input {

            width: 100%;

            height: 44px;

            padding: 0 13px;

            background: rgba(2, 9, 18, 0.85);

            border: 1px solid #203b52;

            border-radius: 10px;

            outline: none;

            color: #e9f8ff;

            transition: 0.15s;
        }


        input:focus {

            border-color: #27bfff;

            box-shadow:
                0 0 0 3px rgba(39, 191, 255, 0.08);
        }


        button {

            width: 100%;

            height: 44px;

            margin-top: 9px;

            border: 1px solid #27c6ff;

            border-radius: 10px;

            background:
                linear-gradient(
                    135deg,
                    #16bfff,
                    #286eff
                );

            color: #fff;

            font-size: 10px;

            font-weight: bold;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;

            box-shadow:
                0 0 20px rgba(31, 164, 255, 0.13);
        }


        button:hover {

            filter: brightness(1.08);

            box-shadow:
                0 0 28px rgba(31, 164, 255, 0.25);
        }


        .error {

            margin-top: 12px;

            padding: 10px;

            border: 1px solid rgba(255, 80, 100, 0.18);

            border-radius: 8px;

            background: rgba(80, 10, 20, 0.2);

            color: #ff7d8b;

            font-size: 11px;
        }

    </style>

</head>


<body>


<div class="login">


    <h1>
        GENGA Admin
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
                url_for(
                    "admin_panel"
                )
            )


        return render_template_string(

            ADMIN_LOGIN_HTML,

            error="Invalid password."

        )


    if session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for(
                "admin_panel"
            )
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

        key=lambda item:
            item["created"],

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

            action_html = """

                <span class="approved">
                    APPROVED
                </span>

            """

        else:

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
                    colspan="4"
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

            background:
                radial-gradient(
                    circle at top,
                    rgba(0, 174, 255, 0.12),
                    transparent 40%
                ),
                #050911;

            color: #e9f7ff;

            font-family:
                Arial,
                Helvetica,
                sans-serif;
        }}


        .container {{

            width: min(
                1100px,
                calc(100% - 24px)
            );

            margin: 45px auto;
        }}


        .top {{

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 22px;

            border: 1px solid rgba(70, 170, 255, 0.16);

            border-radius: 16px;

            background:
                linear-gradient(
                    145deg,
                    rgba(12, 25, 43, 0.94),
                    rgba(5, 11, 21, 0.94)
                );

            box-shadow:
                0 0 35px rgba(0, 128, 255, 0.05);

            position: relative;
        }}


        .top::before {{

            content: "";

            position: absolute;

            left: 0;

            top: 0;

            width: 100%;

            height: 2px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    #29c8ff,
                    transparent
                );
        }}


        h1 {{

            margin: 0;

            font-size: 23px;

            color: #fff;
        }}


        .sub {{

            margin-top: 5px;

            color: #668196;

            font-size: 11px;
        }}


        .logout {{

            color: #668196;

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: 0.05em;

            transition: 0.15s;
        }}


        .logout:hover {{

            color: #2bcaff;
        }}


        .table-wrap {{

            margin-top: 20px;

            overflow-x: auto;

            padding: 4px;

            border: 1px solid rgba(70, 170, 255, 0.12);

            border-radius: 15px;

            background: rgba(6, 15, 27, 0.88);
        }}


        table {{

            width: 100%;

            border-collapse: collapse;

            min-width: 750px;
        }}


        th {{

            padding: 13px 10px;

            text-align: left;

            border-bottom: 1px solid #1d3549;

            color: #4f7187;

            font-size: 9px;

            text-transform: uppercase;

            letter-spacing: 0.07em;
        }}


        td {{

            padding: 13px 10px;

            border-bottom: 1px solid rgba(48, 102, 139, 0.10);

            font-size: 11px;
        }}


        tr:last-child td {{

            border-bottom: 0;
        }}


        code {{

            color: #8db7cc;

            font-family:
                "Courier New",
                monospace;

            font-size: 10px;
        }}


        .approved {{

            color: #29caff;

            font-size: 10px;

            font-weight: bold;

            text-shadow:
                0 0 10px rgba(41, 202, 255, 0.25);
        }}


        .approve {{

            padding: 7px 12px;

            border: 1px solid #25c7ff;

            border-radius: 7px;

            background:
                linear-gradient(
                    135deg,
                    #16bfff,
                    #286eff
                );

            color: #fff;

            font-size: 9px;

            font-weight: bold;

            cursor: pointer;
        }}


        .approve:hover {{

            filter: brightness(1.1);
        }}


        .empty {{

            padding: 30px;

            text-align: center;

            color: #4d687a;
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
        url_for(
            "admin_panel"
        )
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route(
    "/admin/logout"
)
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

        SOURCE_DATEI

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

@app.route(
    "/health"
)
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
