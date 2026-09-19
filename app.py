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

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"


# ------------------------------------------------------------
# DISCORD
#
# Der Invite bleibt ABSICHTLICH direkt im Code.
# Keine Environment Variable dafür.
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
                    16728064,

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

            color: #e5e5e5;

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
                760px,
                calc(100% - 30px)
            );

            margin: 70px auto;

        }


        /* ====================================================
           HEADER
           ==================================================== */

        header {

            padding-bottom: 25px;

            border-bottom: 1px solid #262626;

            margin-bottom: 35px;
        }


        .brand {

            font-size: 25px;

            font-weight: 700;

            letter-spacing: -0.03em;
        }


        .brand span {

            color: #f04b1c;
        }


        .version {

            margin-top: 6px;

            color: #666;

            font-size: 12px;
        }


        /* ====================================================
           SECTIONS
           ==================================================== */

        section {

            margin-bottom: 42px;
        }


        h2 {

            margin: 0 0 17px;

            font-size: 13px;

            font-weight: 700;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            color: #f04b1c;
        }


        .line {

            border-top: 1px solid #262626;

            margin-bottom: 18px;
        }


        /* ====================================================
           DOWNLOAD
           ==================================================== */

        .download-name {

            font-size: 20px;

            font-weight: 600;
        }


        .download-description {

            margin-top: 7px;

            color: #777;

            line-height: 1.6;
        }


        .file {

            margin-top: 18px;

            padding: 12px;

            border: 1px solid #252525;

            background: #0d0d0d;

            color: #aaa;

            font-family:
                "Courier New",
                monospace;

            font-size: 12px;

            overflow-x: auto;
        }


        .download-button {

            display: inline-flex;

            align-items: center;

            justify-content: center;

            min-width: 150px;

            height: 42px;

            margin-top: 12px;

            padding: 0 18px;

            background: #f04b1c;

            border: 1px solid #f04b1c;

            color: #fff;

            font-size: 11px;

            font-weight: 700;

            letter-spacing: 0.06em;

            text-transform: uppercase;
        }


        .download-button:hover {

            background: #ff5b27;

            border-color: #ff5b27;
        }


        .download-waiting {

            margin-top: 16px;

            color: #666;

            font-size: 12px;

            line-height: 1.6;
        }


        /* ====================================================
           ACCESS
           ==================================================== */

        .access-text {

            color: #777;

            line-height: 1.6;

            margin-bottom: 17px;
        }


        .key-row {

            display: flex;

            gap: 8px;

            max-width: 600px;
        }


        .key-input {

            flex: 1;

            min-width: 0;

            height: 42px;

            padding: 0 12px;

            background: #0b0b0b;

            border: 1px solid #303030;

            outline: none;

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

            height: 42px;

            padding: 0 18px;

            background: #f04b1c;

            border: 1px solid #f04b1c;

            color: #fff;

            font-size: 10px;

            font-weight: 700;

            letter-spacing: 0.06em;

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

            margin-top: 20px;

            padding-top: 18px;

            border-top: 1px solid #222;

            font-size: 12px;
        }


        .discord-label {

            color: #666;

            margin-right: 6px;
        }


        .discord-link {

            color: #aaa;

            font-family:
                "Courier New",
                monospace;
        }


        .discord-link:hover {

            color: #f04b1c;
        }


        /* ====================================================
           MESSAGE
           ==================================================== */

        .message {

            margin-bottom: 30px;

            padding: 12px;

            border-left: 2px solid #f04b1c;

            background: #101010;

            color: #999;

            font-size: 12px;

            line-height: 1.5;
        }


        /* ====================================================
           INFORMATION
           ==================================================== */

        .info {

            border-top: 1px solid #262626;
        }


        .info-row {

            display: flex;

            justify-content: space-between;

            gap: 20px;

            padding: 13px 0;

            border-bottom: 1px solid #202020;
        }


        .info-name {

            color: #666;

            font-size: 11px;

            text-transform: uppercase;

            letter-spacing: 0.05em;
        }


        .info-value {

            color: #aaa;

            text-align: right;

            font-size: 12px;
        }


        /* ====================================================
           FOOTER
           ==================================================== */

        footer {

            padding-top: 20px;

            border-top: 1px solid #262626;

            color: #4d4d4d;

            font-size: 11px;
        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 600px) {

            .page {

                width: calc(100% - 24px);

                margin: 35px auto;
            }


            header {

                margin-bottom: 28px;
            }


            .brand {

                font-size: 22px;
            }


            .key-row {

                flex-direction: column;
            }


            .request-button {

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


        <!--
            DISCORD INVITE ABSICHTLICH DIREKT IM HTML.
            Keine Environment Variable.
        -->

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


                /*
                 * Genau EIN Redirect.
                 *
                 * Danach wird approvalView = true,
                 * wodurch kein weiterer Poll gestartet wird.
                 */

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
     * Nur bei einer noch nicht freigegebenen Anfrage
     * wird der Status geprüft.
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

            background: #090909;

            color: #eee;

            font-family:
                Arial,
                Helvetica,
                sans-serif;
        }


        .login {

            width: min(
                380px,
                calc(100% - 24px)
            );

            border-top: 2px solid #f04b1c;
        }


        h1 {

            margin: 0;

            font-size: 24px;
        }


        p {

            margin: 7px 0 20px;

            color: #666;

            font-size: 12px;
        }


        input {

            width: 100%;

            height: 42px;

            padding: 0 12px;

            background: #0b0b0b;

            border: 1px solid #303030;

            outline: none;

            color: #eee;
        }


        input:focus {

            border-color: #555;
        }


        button {

            width: 100%;

            height: 42px;

            margin-top: 8px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: #fff;

            font-size: 10px;

            font-weight: bold;

            letter-spacing: 0.06em;

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

            background: #090909;

            color: #eee;

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

            padding-bottom: 18px;

            border-bottom: 1px solid #262626;
        }}


        h1 {{

            margin: 0;

            font-size: 23px;
        }}


        .sub {{

            margin-top: 5px;

            color: #666;

            font-size: 11px;
        }}


        .logout {{

            color: #666;

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: 0.05em;
        }}


        .logout:hover {{

            color: #f04b1c;
        }}


        .table-wrap {{

            margin-top: 20px;

            overflow-x: auto;
        }}


        table {{

            width: 100%;

            border-collapse: collapse;

            min-width: 750px;
        }}


        th {{

            padding: 11px 10px;

            text-align: left;

            border-bottom: 1px solid #262626;

            color: #555;

            font-size: 9px;

            text-transform: uppercase;

            letter-spacing: 0.07em;
        }}


        td {{

            padding: 13px 10px;

            border-bottom: 1px solid #1d1d1d;

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

            color: #f04b1c;

            font-size: 10px;

            font-weight: bold;
        }}


        .approve {{

            padding: 7px 11px;

            border: 1px solid #f04b1c;

            background: #f04b1c;

            color: #fff;

            font-size: 9px;

            font-weight: bold;

            cursor: pointer;
        }}


        .approve:hover {{

            background: #ff5b27;
        }}


        .empty {{

            padding: 30px;

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
