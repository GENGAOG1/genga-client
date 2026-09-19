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

app.secret_key = os.environ.get("GENGA_SECRET_KEY", "change-this-secret-key")

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

VALID_KEYS = [
    key.strip()
    for key in os.environ.get("GENGA_VALID_KEYS", "").split(",")
    if key.strip()
]

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

DISCORD_URL = "https://discord.gg/VEEV2gaeB"

ADMIN_URL = "https://genga-client.onrender.com/admin"

# Requests bleiben solange im RAM, wie die Render-Instanz läuft.
PENDING_REQUESTS = {}


# ============================================================
# HELPERS
# ============================================================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))

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
        created = data.get("created", now)

        if now - created > max_age:
            expired.append(request_id)

    for request_id in expired:
        PENDING_REQUESTS.pop(request_id, None)


def send_discord_notification(key, request_id):
    """
    Sendet eine neue Download-Anfrage an Discord.
    """
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL ist nicht gesetzt.")
        return False

    payload = {
        "embeds": [
            {
                "title": "GENGA CLIENT • DOWNLOAD REQUEST",
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

        print("Discord Webhook Status:", response.status_code)

        if response.status_code >= 400:
            print("Discord Webhook Error:", response.text)

        return response.ok

    except Exception as error:
        print("Discord Webhook Exception:", error)
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

        :root {
            --bg: #080808;
            --panel: #101010;
            --panel-2: #131313;
            --border: #292929;

            --text: #f2f2f2;
            --muted: #858585;

            --accent: #ff4a00;
            --accent-hover: #ff5d16;

            --success: #39d98a;
            --danger: #ff4d4d;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            min-height: 100vh;

            background:
                radial-gradient(
                    circle at 50% -20%,
                    rgba(255, 74, 0, 0.10),
                    transparent 42%
                ),
                var(--bg);

            color: var(--text);

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Arial,
                sans-serif;

            line-height: 1.5;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        button,
        input {
            font: inherit;
        }

        /* =====================================================
           NAVBAR
           ===================================================== */

        .navbar {
            width: 100%;
            border-bottom: 1px solid var(--border);
            background: rgba(8, 8, 8, 0.94);
        }

        .navbar-inner {
            max-width: 1180px;
            margin: auto;

            min-height: 72px;

            padding: 0 24px;

            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;

            font-size: 18px;
            font-weight: 800;
            letter-spacing: 0.12em;
        }

        .brand-mark {
            width: 9px;
            height: 30px;

            background: var(--accent);

            transform: skew(-14deg);
        }

        .brand span {
            color: #fff;
        }

        .brand-version {
            color: var(--muted);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
        }

        .nav-status {
            display: flex;
            align-items: center;
            gap: 8px;

            color: var(--muted);

            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .status-dot {
            width: 7px;
            height: 7px;

            border-radius: 50%;
            background: var(--success);
        }

        /* =====================================================
           PAGE
           ===================================================== */

        .container {
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 48px 0 70px;
        }

        /* =====================================================
           HEADER
           ===================================================== */

        .page-header {
            margin-bottom: 30px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 9px;

            margin-bottom: 12px;

            color: var(--accent);

            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .eyebrow-line {
            width: 24px;
            height: 1px;
            background: var(--accent);
        }

        .page-header h1 {
            font-size: clamp(38px, 6vw, 64px);
            line-height: 0.98;

            font-weight: 850;
            letter-spacing: -0.045em;

            margin-bottom: 15px;
        }

        .page-header h1 span {
            color: var(--accent);
        }

        .page-header p {
            max-width: 650px;

            color: var(--muted);

            font-size: 15px;
        }

        /* =====================================================
           TOP CARDS
           ===================================================== */

        .top-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;

            margin-bottom: 14px;
        }

        .panel {
            background: var(--panel);

            border: 1px solid var(--border);

            position: relative;
            overflow: hidden;
        }

        .panel::before {
            content: "";

            position: absolute;
            top: 0;
            left: 0;

            width: 3px;
            height: 100%;

            background: var(--accent);
        }

        .top-card {
            min-height: 270px;

            padding: 30px;

            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .card-label {
            color: var(--accent);

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }

        .top-card h2 {
            margin-top: 12px;

            font-size: 30px;
            line-height: 1.05;

            letter-spacing: -0.025em;
        }

        .top-card p {
            margin-top: 10px;

            color: var(--muted);
            font-size: 14px;

            max-width: 440px;
        }

        /* =====================================================
           ACCESS
           ===================================================== */

        .access-form {
            margin-top: 24px;

            display: flex;
            gap: 8px;
        }

        .key-input {
            width: 100%;

            height: 48px;

            padding: 0 15px;

            color: #fff;
            background: #0a0a0a;

            border: 1px solid #303030;

            outline: none;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .key-input::placeholder {
            color: #5e5e5e;
        }

        .key-input:focus {
            border-color: var(--accent);
            background: #0d0d0d;
        }

        .button {
            height: 48px;

            padding: 0 22px;

            border: 1px solid var(--accent);

            background: var(--accent);
            color: #fff;

            font-size: 12px;
            font-weight: 800;

            letter-spacing: 0.08em;
            text-transform: uppercase;

            cursor: pointer;

            white-space: nowrap;

            transition:
                background 0.15s ease,
                border-color 0.15s ease,
                transform 0.15s ease;
        }

        .button:hover {
            background: var(--accent-hover);
            border-color: var(--accent-hover);

            transform: translateY(-1px);
        }

        .button.secondary {
            background: transparent;
            border-color: #363636;
        }

        .button.secondary:hover {
            background: #171717;
            border-color: #4a4a4a;
        }

        .download-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;

            margin-top: 24px;

            width: 100%;
        }

        /* =====================================================
           APPROVED
           ===================================================== */

        .approved-box {
            margin-top: 22px;

            padding: 16px;

            background: rgba(57, 217, 138, 0.05);
            border: 1px solid rgba(57, 217, 138, 0.25);
        }

        .approved-title {
            color: var(--success);

            font-size: 11px;
            font-weight: 800;

            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        .approved-text {
            margin-top: 5px;

            color: var(--muted);
            font-size: 13px;
        }

        /* =====================================================
           WAITING
           ===================================================== */

        .waiting {
            margin-top: 22px;

            display: flex;
            align-items: center;
            gap: 10px;

            color: var(--muted);

            font-size: 12px;
        }

        .waiting-dot {
            width: 7px;
            height: 7px;

            border-radius: 50%;
            background: var(--accent);
        }

        /* =====================================================
           DISCORD
           ===================================================== */

        .discord-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;

            width: 100%;
            height: 44px;

            margin-top: 10px;

            border: 1px solid #303030;

            background: #0c0c0c;

            color: #e8e8e8;

            font-size: 12px;
            font-weight: 700;

            letter-spacing: 0.05em;
            text-transform: uppercase;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .discord-button:hover {
            border-color: #555;
            background: #151515;
        }

        .discord-icon {
            font-size: 15px;
        }

        /* =====================================================
           INFO SECTION
           ===================================================== */

        .section-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;

            margin: 38px 0 14px;
        }

        .section-heading h2 {
            font-size: 18px;
            font-weight: 800;

            letter-spacing: -0.01em;
        }

        .section-heading span {
            color: #555;

            font-size: 10px;
            font-weight: 700;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
        }

        .info-card {
            min-height: 165px;

            padding: 24px;

            background: var(--panel);

            border: 1px solid var(--border);

            transition:
                border-color 0.15s ease,
                transform 0.15s ease;
        }

        .info-card:hover {
            border-color: #3a3a3a;
            transform: translateY(-2px);
        }

        .info-number {
            color: var(--accent);

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 0.1em;
        }

        .info-card h3 {
            margin-top: 15px;

            font-size: 17px;
            font-weight: 750;
        }

        .info-card p {
            margin-top: 7px;

            color: var(--muted);
            font-size: 13px;
        }

        /* =====================================================
           VERSION / CLIENT INFO
           ===================================================== */

        .details {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;

            margin-top: 14px;

            background: var(--border);
            border: 1px solid var(--border);
        }

        .detail {
            padding: 20px;

            background: var(--panel);
        }

        .detail-label {
            color: #626262;

            font-size: 9px;
            font-weight: 800;

            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .detail-value {
            margin-top: 7px;

            color: #ededed;

            font-size: 14px;
            font-weight: 700;
        }

        /* =====================================================
           ALERT
           ===================================================== */

        .alert {
            margin-bottom: 18px;

            padding: 13px 15px;

            border: 1px solid rgba(255, 74, 0, 0.35);
            background: rgba(255, 74, 0, 0.06);

            color: #ff9b73;

            font-size: 13px;
        }

        /* =====================================================
           FOOTER
           ===================================================== */

        footer {
            margin-top: 55px;
            padding-top: 20px;

            border-top: 1px solid var(--border);

            display: flex;
            align-items: center;
            justify-content: space-between;

            gap: 20px;

            color: #555;

            font-size: 11px;
        }

        footer strong {
            color: #777;
        }

        /* =====================================================
           MOBILE
           ===================================================== */

        @media (max-width: 760px) {

            .container {
                width: min(100% - 22px, 1180px);
                padding-top: 32px;
            }

            .navbar-inner {
                padding: 0 14px;
            }

            .nav-status {
                display: none;
            }

            .top-grid {
                grid-template-columns: 1fr;
            }

            .info-grid {
                grid-template-columns: 1fr;
            }

            .details {
                grid-template-columns: 1fr 1fr;
            }

            .access-form {
                flex-direction: column;
            }

            .access-form .button {
                width: 100%;
            }

            .top-card {
                min-height: auto;
            }

            footer {
                flex-direction: column;
                align-items: flex-start;
            }
        }

        @media (max-width: 430px) {

            .page-header h1 {
                font-size: 42px;
            }

            .top-card {
                padding: 23px;
            }

            .details {
                grid-template-columns: 1fr;
            }
        }

    </style>

</head>

<body>

    <!-- =====================================================
         NAVBAR
         ===================================================== -->

    <nav class="navbar">

        <div class="navbar-inner">

            <a href="/" class="brand">

                <div class="brand-mark"></div>

                <span>GENGA</span>

                <span class="brand-version">
                    1.21.11
                </span>

            </a>

            <div class="nav-status">

                <span class="status-dot"></span>

                System Online

            </div>

        </div>

    </nav>


    <!-- =====================================================
         MAIN
         ===================================================== -->

    <main class="container">


        <!-- HEADER -->

        <header class="page-header">

            <div class="eyebrow">

                <span class="eyebrow-line"></span>

                GENGA CLIENT

            </div>

            <h1>
                Minecraft client.<br>
                <span>Nothing unnecessary.</span>
            </h1>

            <p>
                Access the GENGA Client for Minecraft 1.21.11.
                Enter your access key below to request access to
                the client download.
            </p>

        </header>


        <!-- ALERT -->

        {% if message %}

            <div class="alert">
                {{ message }}
            </div>

        {% endif %}


        <!-- =================================================
             TOP: DOWNLOAD + ACCESS
             ================================================= -->

        <section class="top-grid">


            <!-- DOWNLOAD -->

            <div class="panel top-card">

                <div>

                    <div class="card-label">
                        01 / DOWNLOAD
                    </div>

                    <h2>
                        GENGA Client
                    </h2>

                    <p>
                        Minecraft 1.21.11 client build.
                        The download becomes available after
                        your access request has been approved.
                    </p>

                </div>


                {% if download_ready %}

                    <div class="approved-box">

                        <div class="approved-title">
                            Access granted
                        </div>

                        <div class="approved-text">
                            Your request has been approved.
                            The client is ready to download.
                        </div>

                    </div>

                    <a
                        class="button download-button"
                        href="{{ url_for('download', request_id=request_id) }}"
                    >
                        Download Client
                    </a>

                {% else %}

                    <div class="waiting">

                        <span class="waiting-dot"></span>

                        Waiting for access approval

                    </div>

                {% endif %}

            </div>


            <!-- ACCESS -->

            <div class="panel top-card">

                <div>

                    <div class="card-label">
                        02 / ACCESS
                    </div>

                    <h2>
                        Enter your key
                    </h2>

                    <p>
                        Enter your valid GENGA access key.
                        A request will then be sent for approval.
                    </p>

                </div>


                {% if not download_ready %}

                    <form
                        class="access-form"
                        method="POST"
                        action="{{ url_for('request_download') }}"
                    >

                        <input
                            class="key-input"
                            type="text"
                            name="key"
                            placeholder="GENGA-XXXX-XXXX"
                            autocomplete="off"
                            required
                        >

                        <button
                            class="button"
                            type="submit"
                        >
                            Request
                        </button>

                    </form>

                {% else %}

                    <div class="approved-box">

                        <div class="approved-title">
                            Verified
                        </div>

                        <div class="approved-text">
                            Your access request has already been
                            approved for this session.
                        </div>

                    </div>

                {% endif %}


                <!-- DISCORD BUTTON -->

                <a
                    class="discord-button"
                    href="{{ discord_url }}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="discord-icon">◈</span>
                    Join GENGA Discord
                </a>

            </div>

        </section>


        <!-- =================================================
             INFORMATION
             ================================================= -->

        <div class="section-heading">

            <h2>
                Information
            </h2>

            <span>
                Client overview
            </span>

        </div>


        <section class="info-grid">


            <div class="info-card">

                <div class="info-number">
                    01
                </div>

                <h3>
                    Clean Interface
                </h3>

                <p>
                    A compact client interface focused on
                    functionality without unnecessary visual clutter.
                </p>

            </div>


            <div class="info-card">

                <div class="info-number">
                    02
                </div>

                <h3>
                    Modular
                </h3>

                <p>
                    Client functionality is organized into modules
                    that can be enabled and configured individually.
                </p>

            </div>


            <div class="info-card">

                <div class="info-number">
                    03
                </div>

                <h3>
                    Minecraft 1.21.11
                </h3>

                <p>
                    This download page is configured for the
                    GENGA Client 1.21.11 build.
                </p>

            </div>

        </section>


        <!-- =================================================
             DETAILS
             ================================================= -->

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


    <!-- =====================================================
         APPROVAL SCRIPT
         ===================================================== -->

    <script>

        const requestId = {{ request_id|tojson }};

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


                const data = await response.json();


                if (data.status === "approved") {

                    /*
                     * IMPORTANT:
                     *
                     * Stop checking immediately.
                     * Then perform exactly ONE navigation
                     * to the approved page.
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

            } catch (error) {

                console.log(
                    "Approval status check failed:",
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

            setTimeout(checkStatus, 2000);
        }


        /*
         * Start checking only while approval is pending.
         *
         * Once approved:
         *
         * pending page
         *       ↓
         * ONE navigation
         *       ↓
         * approved page
         *       ↓
         * NO MORE POLLING
         */

        if (requestId && !approvalView) {
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

    request_id = request.args.get("request")

    message = None

    if request.args.get("error") == "invalid":
        message = "The entered access key is invalid."

    elif request.args.get("error") == "missing":
        message = "Please enter an access key."

    elif request.args.get("error") == "expired":
        message = "This download request no longer exists."

    elif request.args.get("error") == "notapproved":
        message = "Your request has not been approved yet."

    download_ready = False

    if request_id:

        request_data = PENDING_REQUESTS.get(request_id)

        if request_data:

            if request_data.get("approved") is True:
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

@app.route("/request-download", methods=["POST"])
def request_download():

    cleanup_requests()

    key = request.form.get("key", "").strip()


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


    request_id = str(uuid.uuid4())


    PENDING_REQUESTS[request_id] = {

        "key": key,

        "approved": False,

        "created": time.time(),

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
# STATUS
# ============================================================

@app.route("/status/<request_id>", methods=["GET"])
def status(request_id):

    request_data = PENDING_REQUESTS.get(request_id)


    if not request_data:

        return jsonify({
            "status": "not_found"
        }), 404


    if request_data.get("approved") is True:

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

            background: #080808;
            color: #fff;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .box {
            width: min(420px, calc(100% - 30px));

            padding: 30px;

            background: #101010;

            border: 1px solid #292929;

            position: relative;
        }

        .box::before {
            content: "";

            position: absolute;

            top: 0;
            left: 0;

            width: 3px;
            height: 100%;

            background: #ff4a00;
        }

        .label {
            color: #ff4a00;

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 0.15em;
            text-transform: uppercase;
        }

        h1 {
            margin: 10px 0;

            font-size: 30px;
        }

        p {
            color: #777;
            font-size: 13px;
        }

        input {
            width: 100%;

            height: 48px;

            margin-top: 20px;

            padding: 0 14px;

            background: #080808;

            color: #fff;

            border: 1px solid #303030;

            outline: none;
        }

        input:focus {
            border-color: #ff4a00;
        }

        button {
            width: 100%;

            height: 48px;

            margin-top: 10px;

            border: 1px solid #ff4a00;

            background: #ff4a00;

            color: #fff;

            font-weight: 800;

            text-transform: uppercase;

            letter-spacing: 0.08em;

            cursor: pointer;
        }

        button:hover {
            background: #ff5d16;
        }

        .error {
            margin-top: 14px;

            color: #ff6666;

            font-size: 12px;
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


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_panel")
            )

        return render_template_string(
            ADMIN_LOGIN_HTML,
            error="Invalid password."
        )


    if session.get("admin_logged_in"):

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

@app.route("/admin/panel", methods=["GET"])
@admin_required
def admin_panel():

    cleanup_requests()

    requests_list = []

    for request_id, data in PENDING_REQUESTS.items():

        requests_list.append({
            "id": request_id,
            "key": data.get("key", ""),
            "approved": data.get("approved", False),
            "created": data.get("created", 0)
        })


    requests_list.sort(
        key=lambda item: item["created"],
        reverse=True
    )


    rows = ""


    for item in requests_list:

        created_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(item["created"])
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

            background: #080808;
            color: #eee;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

        }}

        .container {{

            width: min(1250px, calc(100% - 30px));

            margin: auto;

            padding: 40px 0 60px;

        }}

        .top {{

            display: flex;

            align-items: center;

            justify-content: space-between;

            margin-bottom: 25px;

        }}

        h1 {{

            margin: 0;

            font-size: 32px;

        }}

        .subtitle {{

            margin-top: 5px;

            color: #666;

            font-size: 13px;

        }}

        .logout {{

            color: #999;

            text-decoration: none;

            font-size: 12px;

            border: 1px solid #292929;

            padding: 10px 15px;

        }}

        .logout:hover {{

            color: #fff;

            border-color: #444;

        }}

        .table-wrap {{

            overflow-x: auto;

            border: 1px solid #292929;

        }}

        table {{

            width: 100%;

            border-collapse: collapse;

            min-width: 900px;

        }}

        th {{

            text-align: left;

            padding: 15px;

            color: #666;

            background: #101010;

            font-size: 10px;

            text-transform: uppercase;

            letter-spacing: 0.1em;

        }}

        td {{

            padding: 15px;

            border-top: 1px solid #202020;

            font-size: 12px;

            background: #0d0d0d;

        }}

        code {{

            color: #bbb;

        }}

        .approved {{

            color: #39d98a;

            font-weight: 800;

        }}

        .pending {{

            color: #ff7a4d;

            font-weight: 800;

        }}

        .done {{

            color: #555;

            font-size: 10px;

            font-weight: 800;

        }}

        .approve {{

            border: 1px solid #ff4a00;

            background: #ff4a00;

            color: white;

            padding: 9px 14px;

            font-size: 10px;

            font-weight: 800;

            cursor: pointer;

        }}

        .approve:hover {{

            background: #ff5d16;

        }}

        .empty {{

            padding: 40px;

            text-align: center;

            color: #666;

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

                    {rows if rows else '''
                        <tr>
                            <td colspan="5" class="empty">
                                No download requests yet.
                            </td>
                        </tr>
                    '''}

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

    request_data = PENDING_REQUESTS.get(request_id)


    if request_data:

        request_data["approved"] = True

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

    request_data = PENDING_REQUESTS.get(request_id)


    if not request_data:

        return redirect(
            url_for(
                "index",
                error="expired"
            )
        )


    if request_data.get("approved") is not True:

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


    if not os.path.isfile(file_path):

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
