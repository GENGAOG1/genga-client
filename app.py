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


DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

DISCORD_URL = "https://discord.gg/sw7zNs9T58"

ADMIN_URL = "https://genga-client.onrender.com/admin"


# Requests bleiben im RAM, solange die Render-Instanz läuft.
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
            expired.append(request_id)

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

                "title": "GENGA CLIENT / DOWNLOAD REQUEST",

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

        /* ====================================================
           BASE
           ==================================================== */

        :root {

            --background: #090909;

            --surface: #101010;

            --surface-hover: #141414;

            --border: #252525;

            --border-light: #303030;

            --text: #eeeeee;

            --text-soft: #aaaaaa;

            --text-muted: #686868;

            --orange: #ff4b00;

            --orange-hover: #ff5b16;

            --green: #42d392;

            --red: #ff5757;

        }


        * {

            box-sizing: border-box;

            margin: 0;

            padding: 0;

        }


        html {

            background: var(--background);

        }


        body {

            min-height: 100vh;

            background: var(--background);

            color: var(--text);

            font-family:

                Inter,

                -apple-system,

                BlinkMacSystemFont,

                "Segoe UI",

                Roboto,

                Arial,

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
           NAVBAR
           ==================================================== */

        .navbar {

            height: 64px;

            border-bottom: 1px solid var(--border);

            background: #0b0b0b;

        }


        .navbar-inner {

            width: min(
                1100px,
                calc(100% - 32px)
            );

            height: 100%;

            margin: auto;

            display: flex;

            align-items: center;

            justify-content: space-between;

        }


        .logo {

            display: flex;

            align-items: center;

            gap: 10px;

            font-size: 15px;

            font-weight: 800;

            letter-spacing: 0.14em;

        }


        .logo-bar {

            width: 4px;

            height: 20px;

            background: var(--orange);

        }


        .version {

            color: var(--text-muted);

            font-size: 10px;

            font-weight: 600;

            letter-spacing: 0.08em;

        }


        .online {

            display: flex;

            align-items: center;

            gap: 7px;

            color: var(--text-muted);

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: 0.08em;

        }


        .online-dot {

            width: 6px;

            height: 6px;

            background: var(--green);

            border-radius: 50%;

        }


        /* ====================================================
           PAGE
           ==================================================== */

        .page {

            width: min(
                1100px,
                calc(100% - 32px)
            );

            margin: auto;

            padding: 42px 0 70px;

        }


        /* ====================================================
           SMALL HEADER
           ==================================================== */

        .header {

            margin-bottom: 28px;

        }


        .header-label {

            color: var(--orange);

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 0.14em;

            text-transform: uppercase;

            margin-bottom: 8px;

        }


        .header h1 {

            font-size: 32px;

            line-height: 1.1;

            font-weight: 750;

            letter-spacing: -0.025em;

        }


        .header p {

            margin-top: 8px;

            color: var(--text-muted);

            max-width: 600px;

            font-size: 13px;

        }


        /* ====================================================
           ALERT
           ==================================================== */

        .alert {

            margin-bottom: 16px;

            padding: 12px 14px;

            border: 1px solid #49271b;

            background: #160e0a;

            color: #ff9a72;

            font-size: 12px;

        }


        /* ====================================================
           MAIN GRID
           ==================================================== */

        .main-grid {

            display: grid;

            grid-template-columns: 1fr 1fr;

            gap: 1px;

            background: var(--border);

            border: 1px solid var(--border);

        }


        .section {

            min-height: 300px;

            padding: 26px;

            background: var(--surface);

        }


        .section:hover {

            background: #111111;

        }


        .section-header {

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding-bottom: 18px;

            border-bottom: 1px solid var(--border);

        }


        .section-title {

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 0.12em;

            text-transform: uppercase;

        }


        .section-number {

            color: var(--text-muted);

            font-size: 10px;

            font-weight: 700;

        }


        .section-content {

            padding-top: 24px;

        }


        .section-content h2 {

            font-size: 23px;

            font-weight: 700;

            letter-spacing: -0.02em;

        }


        .section-content p {

            margin-top: 8px;

            max-width: 430px;

            color: var(--text-muted);

            font-size: 13px;

            line-height: 1.65;

        }


        /* ====================================================
           DOWNLOAD
           ==================================================== */

        .download-state {

            margin-top: 30px;

            padding: 15px;

            border: 1px solid var(--border);

            background: #0b0b0b;

        }


        .download-state-label {

            color: var(--text-muted);

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 0.12em;

            text-transform: uppercase;

        }


        .download-state-value {

            margin-top: 6px;

            font-size: 13px;

            font-weight: 700;

        }


        .download-state-value.waiting {

            color: #c6c6c6;

        }


        .download-state-value.ready {

            color: var(--green);

        }


        .download-button {

            width: 100%;

            height: 46px;

            margin-top: 10px;

            display: flex;

            align-items: center;

            justify-content: center;

            border: 1px solid var(--orange);

            background: var(--orange);

            color: white;

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 0.09em;

            text-transform: uppercase;

        }


        .download-button:hover {

            background: var(--orange-hover);

            border-color: var(--orange-hover);

        }


        /* ====================================================
           ACCESS
           ==================================================== */

        .key-form {

            margin-top: 27px;

        }


        .key-label {

            display: block;

            margin-bottom: 7px;

            color: var(--text-muted);

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 0.1em;

            text-transform: uppercase;

        }


        .key-row {

            display: flex;

            gap: 7px;

        }


        .key-input {

            min-width: 0;

            flex: 1;

            height: 46px;

            padding: 0 13px;

            background: #0a0a0a;

            color: white;

            border: 1px solid var(--border-light);

            outline: none;

            font-size: 12px;

        }


        .key-input:focus {

            border-color: var(--orange);

        }


        .key-input::placeholder {

            color: #4e4e4e;

        }


        .request-button {

            height: 46px;

            padding: 0 19px;

            border: 1px solid var(--orange);

            background: var(--orange);

            color: white;

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;

        }


        .request-button:hover {

            background: var(--orange-hover);

            border-color: var(--orange-hover);

        }


        /* ====================================================
           APPROVED
           ==================================================== */

        .approved {

            margin-top: 27px;

            padding: 14px;

            border-left: 3px solid var(--green);

            background: #0c1410;

        }


        .approved-title {

            color: var(--green);

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 0.1em;

            text-transform: uppercase;

        }


        .approved-text {

            margin-top: 5px;

            color: var(--text-muted);

            font-size: 12px;

        }


        /* ====================================================
           WAITING
           ==================================================== */

        .waiting {

            margin-top: 27px;

            display: flex;

            align-items: center;

            gap: 9px;

            color: var(--text-muted);

            font-size: 11px;

        }


        .waiting-line {

            width: 16px;

            height: 1px;

            background: var(--orange);

        }


        /* ====================================================
           DISCORD
           ==================================================== */

        .discord {

            margin-top: 12px;

            width: 100%;

            height: 42px;

            display: flex;

            align-items: center;

            justify-content: center;

            border: 1px solid var(--border-light);

            background: #0b0b0b;

            color: #c8c8c8;

            font-size: 10px;

            font-weight: 750;

            letter-spacing: 0.07em;

            text-transform: uppercase;

        }


        .discord:hover {

            background: #151515;

            color: white;

            border-color: #414141;

        }


        /* ====================================================
           INFORMATION
           ==================================================== */

        .information {

            margin-top: 34px;

        }


        .information-header {

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding-bottom: 12px;

            border-bottom: 1px solid var(--border);

        }


        .information-header h2 {

            font-size: 16px;

            font-weight: 750;

        }


        .information-header span {

            color: var(--text-muted);

            font-size: 9px;

            font-weight: 700;

            letter-spacing: 0.1em;

            text-transform: uppercase;

        }


        .info-list {

            display: grid;

            grid-template-columns: repeat(3, 1fr);

            gap: 1px;

            margin-top: 1px;

            background: var(--border);

            border: 1px solid var(--border);

        }


        .info-item {

            padding: 22px;

            background: var(--surface);

        }


        .info-item:hover {

            background: var(--surface-hover);

        }


        .info-item-label {

            color: var(--orange);

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 0.1em;

            text-transform: uppercase;

        }


        .info-item h3 {

            margin-top: 11px;

            font-size: 15px;

            font-weight: 700;

        }


        .info-item p {

            margin-top: 6px;

            color: var(--text-muted);

            font-size: 12px;

            line-height: 1.6;

        }


        /* ====================================================
           CLIENT DETAILS
           ==================================================== */

        .details {

            display: grid;

            grid-template-columns: repeat(4, 1fr);

            margin-top: 1px;

            gap: 1px;

            background: var(--border);

            border: 1px solid var(--border);

        }


        .detail {

            padding: 17px 20px;

            background: var(--surface);

        }


        .detail-label {

            color: #555;

            font-size: 8px;

            font-weight: 800;

            letter-spacing: 0.12em;

            text-transform: uppercase;

        }


        .detail-value {

            margin-top: 5px;

            color: #d8d8d8;

            font-size: 12px;

            font-weight: 700;

        }


        /* ====================================================
           FOOTER
           ==================================================== */

        footer {

            margin-top: 30px;

            padding-top: 16px;

            border-top: 1px solid var(--border);

            display: flex;

            align-items: center;

            justify-content: space-between;

            color: #505050;

            font-size: 10px;

        }


        footer strong {

            color: #777;

        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 760px) {

            .page {

                width: min(
                    100% - 20px,
                    1100px
                );

                padding-top: 30px;

            }


            .navbar-inner {

                width: min(
                    100% - 20px,
                    1100px
                );

            }


            .main-grid {

                grid-template-columns: 1fr;

            }


            .info-list {

                grid-template-columns: 1fr;

            }


            .details {

                grid-template-columns: 1fr 1fr;

            }


            .key-row {

                flex-direction: column;

            }


            .request-button {

                width: 100%;

            }


            .online {

                display: none;

            }

        }


        @media (max-width: 430px) {

            .header h1 {

                font-size: 27px;

            }


            .section {

                padding: 21px;

            }


            .details {

                grid-template-columns: 1fr;

            }


            footer {

                flex-direction: column;

                align-items: flex-start;

                gap: 7px;

            }

        }

    </style>

</head>


<body>


    <!-- ====================================================
         NAVIGATION
         ==================================================== -->

    <nav class="navbar">

        <div class="navbar-inner">

            <a
                href="/"
                class="logo"
            >

                <span class="logo-bar"></span>

                <span>GENGA</span>

                <span class="version">
                    1.21.11
                </span>

            </a>


            <div class="online">

                <span class="online-dot"></span>

                Online

            </div>

        </div>

    </nav>


    <!-- ====================================================
         PAGE
         ==================================================== -->

    <main class="page">


        <!-- HEADER -->

        <header class="header">

            <div class="header-label">
                GENGA CLIENT
            </div>

            <h1>
                Client access
            </h1>

            <p>
                Access and download the GENGA Client
                for Minecraft 1.21.11.
            </p>

        </header>


        <!-- ERROR -->

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

            <div class="section">

                <div class="section-header">

                    <div class="section-title">
                        Download
                    </div>

                    <div class="section-number">
                        01
                    </div>

                </div>


                <div class="section-content">

                    <h2>
                        GENGA Client
                    </h2>

                    <p>
                        Minecraft 1.21.11 client build.
                        The download becomes available
                        after your access request has
                        been approved.
                    </p>


                    {% if download_ready %}

                        <div class="approved">

                            <div class="approved-title">
                                Access granted
                            </div>

                            <div class="approved-text">
                                Your request has been approved.
                            </div>

                        </div>


                        <a
                            class="download-button"
                            href="{{ url_for(
                                'download',
                                request_id=request_id
                            ) }}"
                        >
                            Download client
                        </a>

                    {% else %}

                        <div class="download-state">

                            <div class="download-state-label">
                                Status
                            </div>

                            <div class="download-state-value waiting">
                                Waiting for approval
                            </div>

                        </div>

                    {% endif %}

                </div>

            </div>


            <!-- ACCESS -->

            <div class="section">

                <div class="section-header">

                    <div class="section-title">
                        Access
                    </div>

                    <div class="section-number">
                        02
                    </div>

                </div>


                <div class="section-content">

                    <h2>
                        Access key
                    </h2>

                    <p>
                        Enter your valid GENGA access key
                        to create a download request.
                    </p>


                    {% if not download_ready %}

                        <form
                            class="key-form"
                            method="POST"
                            action="{{ url_for(
                                'request_download'
                            ) }}"
                        >

                            <label class="key-label">
                                Access key
                            </label>


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

                        <div class="approved">

                            <div class="approved-title">
                                Verified
                            </div>

                            <div class="approved-text">
                                This access request has been approved.
                            </div>

                        </div>

                    {% endif %}


                    <a
                        class="discord"
                        href="{{ discord_url }}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Join GENGA Discord
                    </a>

                </div>

            </div>

        </section>


        <!-- =================================================
             INFORMATION
             ================================================= -->

        <section class="information">

            <div class="information-header">

                <h2>
                    Information
                </h2>

                <span>
                    Client overview
                </span>

            </div>


            <div class="info-list">


                <div class="info-item">

                    <div class="info-item-label">
                        Interface
                    </div>

                    <h3>
                        Clean UI
                    </h3>

                    <p>
                        A compact interface designed
                        around the GENGA client.
                    </p>

                </div>


                <div class="info-item">

                    <div class="info-item-label">
                        Modules
                    </div>

                    <h3>
                        Modular system
                    </h3>

                    <p>
                        Client functionality is organized
                        into configurable modules.
                    </p>

                </div>


                <div class="info-item">

                    <div class="info-item-label">
                        Version
                    </div>

                    <h3>
                        Minecraft 1.21.11
                    </h3>

                    <p>
                        This website provides access
                        to the GENGA 1.21.11 build.
                    </p>

                </div>


            </div>


            <!-- DETAILS -->

            <div class="details">


                <div class="detail">

                    <div class="detail-label">
                        Client
                    </div>

                    <div class="detail-value">
                        GENGA Client
                    </div>

                </div>


                <div class="detail">

                    <div class="detail-label">
                        Version
                    </div>

                    <div class="detail-value">
                        1.21.11
                    </div>

                </div>


                <div class="detail">

                    <div class="detail-label">
                        Loader
                    </div>

                    <div class="detail-value">
                        Fabric
                    </div>

                </div>


                <div class="detail">

                    <div class="detail-label">
                        Access
                    </div>

                    <div class="detail-value">
                        Key Required
                    </div>

                </div>


            </div>

        </section>


        <!-- =================================================
             FOOTER
             ================================================= -->

        <footer>

            <div>
                <strong>GENGA Client</strong>
                &nbsp; / &nbsp;
                Minecraft 1.21.11
            </div>

            <div>
                Access system
            </div>

        </footer>


    </main>


    <!-- ====================================================
         APPROVAL CHECK
         ==================================================== -->

    <script>

        const requestId =
            {{ request_id|tojson }};


        const approvalView =
            {{ approval_view|tojson }};


        let approvalHandled = false;


        async function checkStatus() {

            /*
             * Kein Request vorhanden.
             */

            if (!requestId) {
                return;
            }


            /*
             * Diese Seite wurde bereits nach
             * der Freigabe geladen.
             *
             * Deshalb NICHT erneut pollen.
             */

            if (approvalView) {
                return;
            }


            /*
             * Verhindert doppelte Weiterleitungen.
             */

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


                /*
                 * APPROVED
                 *
                 * Hier passiert genau EIN
                 * Seitenwechsel.
                 */

                if (
                    data.status === "approved"
                ) {

                    approvalHandled = true;


                    /*
                     * Timer wird nicht mehr
                     * gestartet.
                     */

                    window.location.replace(

                        "/?request=" +
                        encodeURIComponent(requestId) +
                        "&approved=1"

                    );


                    return;

                }


                /*
                 * Noch nicht genehmigt.
                 * Erst jetzt wird der nächste
                 * Check geplant.
                 */

                scheduleNextCheck();


            } catch (error) {

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
         * Polling wird ausschließlich auf
         * der wartenden Seite gestartet.
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

        "created": time.time(),

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
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

        }


        .box {

            width: min(
                400px,
                calc(100% - 30px)
            );

            padding: 28px;

            background: #101010;

            border: 1px solid #252525;

            position: relative;

        }


        .box::before {

            content: "";

            position: absolute;

            top: 0;

            left: 0;

            width: 3px;

            height: 100%;

            background: #ff4b00;

        }


        .label {

            color: #ff4b00;

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 0.14em;

            text-transform: uppercase;

        }


        h1 {

            margin: 9px 0 6px;

            font-size: 27px;

        }


        p {

            color: #666;

            font-size: 12px;

        }


        input {

            width: 100%;

            height: 45px;

            margin-top: 20px;

            padding: 0 13px;

            background: #090909;

            color: #fff;

            border: 1px solid #303030;

            outline: none;

        }


        input:focus {

            border-color: #ff4b00;

        }


        button {

            width: 100%;

            height: 45px;

            margin-top: 8px;

            border: 1px solid #ff4b00;

            background: #ff4b00;

            color: white;

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 0.08em;

            text-transform: uppercase;

            cursor: pointer;

        }


        button:hover {

            background: #ff5b16;

        }


        .error {

            margin-top: 12px;

            color: #ff6666;

            font-size: 11px;

        }

    </style>

</head>


<body>


    <div class="box">

        <div class="label">
            GENGA / ADMIN
        </div>


        <h1>
            Admin Panel
        </h1>


        <p>
            Sign in to manage download requests.
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


    for request_id, data in PENDING_REQUESTS.items():

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

            status_html = """

                <span class="approved">
                    APPROVED
                </span>

            """

        else:

            status_html = """

                <span class="pending">
                    PENDING
                </span>

            """


        if item["approved"]:

            action_html = """

                <span class="done">
                    ACCESS GRANTED
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
                    <code>
                        {item['id']}
                    </code>
                </td>

                <td>
                    <code>
                        {item['key']}
                    </code>
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


    admin_html = f"""

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GENGA Admin Panel</title>


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
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

        }}


        .container {{

            width: min(
                1200px,
                calc(100% - 30px)
            );

            margin: auto;

            padding: 40px 0 60px;

        }}


        .top {{

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-bottom: 22px;

        }}


        h1 {{

            margin: 0;

            font-size: 28px;

        }}


        .subtitle {{

            margin-top: 5px;

            color: #666;

            font-size: 12px;

        }}


        .logout {{

            color: #888;

            text-decoration: none;

            font-size: 10px;

            font-weight: 700;

            letter-spacing: 0.07em;

            text-transform: uppercase;

            border: 1px solid #292929;

            padding: 9px 13px;

        }}


        .logout:hover {{

            color: #fff;

            border-color: #444;

        }}


        .table-wrap {{

            overflow-x: auto;

            border: 1px solid #252525;

        }}


        table {{

            width: 100%;

            border-collapse: collapse;

            min-width: 900px;

        }}


        th {{

            text-align: left;

            padding: 13px;

            color: #555;

            background: #101010;

            font-size: 9px;

            text-transform: uppercase;

            letter-spacing: 0.1em;

        }}


        td {{

            padding: 13px;

            border-top: 1px solid #202020;

            font-size: 11px;

            background: #0d0d0d;

        }}


        code {{

            color: #aaa;

        }}


        .approved {{

            color: #42d392;

            font-weight: 800;

        }}


        .pending {{

            color: #ff774d;

            font-weight: 800;

        }}


        .done {{

            color: #555;

            font-size: 9px;

            font-weight: 800;

        }}


        .approve {{

            border: 1px solid #ff4b00;

            background: #ff4b00;

            color: white;

            padding: 8px 12px;

            font-size: 9px;

            font-weight: 800;

            letter-spacing: 0.06em;

            cursor: pointer;

        }}


        .approve:hover {{

            background: #ff5b16;

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

                <div class="subtitle">
                    Download request management
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

                    {
                        rows if rows else
                        '''
                        <tr>
                            <td
                                colspan="5"
                                class="empty"
                            >
                                No download requests yet.
                            </td>
                        </tr>
                        '''
                    }

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

        request_data["approved"] = True


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
        url_for(
            "admin"
        )
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
