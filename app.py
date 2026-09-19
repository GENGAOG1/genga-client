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
# Configuration
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_PATH = os.path.join(BASE_DIR, DOWNLOAD_DATEI)

# ------------------------------------------------------------
# Temporary request storage
# ------------------------------------------------------------

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


def cleanup_old_requests():
    """
    Removes requests older than 24 hours.
    """
    now = time.time()
    expired = []

    for request_id, data in PENDING_REQUESTS.items():
        created = data.get("created", now)

        if now - created > 86400:
            expired.append(request_id)

    for request_id in expired:
        PENDING_REQUESTS.pop(request_id, None)


# ============================================================
# MAIN PAGE
# ============================================================

MAIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#090807"
    >

    <title>GENGA Client</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --bg: #090807;
            --bg-soft: #0e0c0a;
            --panel: #11100e;
            --panel-2: #151310;
            --border: #292522;
            --border-light: #37312c;

            --orange: #ff4b00;
            --orange-light: #ff641a;
            --red: #e83218;

            --text: #f2eee9;
            --text-soft: #aaa39d;
            --text-muted: #706a65;

            --success: #72d572;
            --danger: #ff4949;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            min-height: 100vh;
            background:
                radial-gradient(
                    circle at 50% -20%,
                    rgba(255, 75, 0, 0.09),
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

            -webkit-font-smoothing: antialiased;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        button,
        input {
            font: inherit;
        }

        .page {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
            padding: 26px 0 50px;
        }

        /* ====================================================
           TOP BAR
           ==================================================== */

        .topbar {
            height: 58px;
            display: flex;
            align-items: center;
            justify-content: space-between;

            border-bottom: 1px solid var(--border);

            margin-bottom: 42px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 11px;
        }

        .brand-mark {
            width: 27px;
            height: 27px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: var(--orange);
            color: #0a0807;

            font-size: 13px;
            font-weight: 900;

            clip-path: polygon(
                0 0,
                100% 0,
                100% 72%,
                72% 100%,
                0 100%
            );
        }

        .brand-name {
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 0.18em;
        }

        .brand-version {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            margin-left: 4px;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;

            color: var(--text-muted);

            font-size: 11px;
            font-weight: 700;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--orange);
            box-shadow: 0 0 0 3px rgba(255, 75, 0, 0.08);
        }

        /* ====================================================
           HERO
           ==================================================== */

        .hero {
            display: grid;
            grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.85fr);
            gap: 18px;

            margin-bottom: 18px;
        }

        .hero-main {
            position: relative;

            min-height: 360px;

            display: flex;
            flex-direction: column;
            justify-content: flex-end;

            padding: 38px;

            background: var(--panel);

            border: 1px solid var(--border);

            overflow: hidden;
        }

        .hero-main::before {
            content: "";

            position: absolute;

            left: 0;
            top: 0;
            bottom: 0;

            width: 3px;

            background: var(--orange);
        }

        .hero-main::after {
            content: "G";

            position: absolute;

            right: 20px;
            top: -30px;

            font-size: 260px;
            line-height: 1;

            font-weight: 900;

            color: rgba(255, 75, 0, 0.025);

            pointer-events: none;
        }

        .eyebrow {
            position: relative;
            z-index: 1;

            color: var(--orange);

            font-size: 11px;
            font-weight: 800;

            letter-spacing: 0.18em;
            text-transform: uppercase;

            margin-bottom: 15px;
        }

        .hero h1 {
            position: relative;
            z-index: 1;

            font-size: clamp(42px, 6vw, 70px);
            line-height: 0.95;

            font-weight: 900;
            letter-spacing: -0.055em;

            margin-bottom: 18px;
        }

        .hero-description {
            position: relative;
            z-index: 1;

            max-width: 570px;

            color: var(--text-soft);

            font-size: 15px;
            line-height: 1.65;
        }

        .hero-meta {
            position: relative;
            z-index: 1;

            display: flex;
            align-items: center;
            gap: 10px;

            margin-top: 28px;

            color: var(--text-muted);

            font-size: 10px;
            font-weight: 700;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .meta-line {
            width: 22px;
            height: 1px;
            background: var(--orange);
        }

        /* ====================================================
           ACCESS PANEL
           ==================================================== */

        .access {
            background: var(--panel);

            border: 1px solid var(--border);

            padding: 27px;

            display: flex;
            flex-direction: column;
        }

        .panel-heading {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;

            margin-bottom: 26px;
        }

        .panel-label {
            color: var(--text-muted);

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 0.15em;
            text-transform: uppercase;
        }

        .panel-number {
            color: var(--orange);

            font-size: 10px;
            font-weight: 800;
        }

        .access h2 {
            font-size: 23px;
            font-weight: 800;
            letter-spacing: -0.025em;

            margin-bottom: 9px;
        }

        .access-text {
            color: var(--text-muted);

            font-size: 13px;
            line-height: 1.55;

            margin-bottom: 24px;
        }

        .key-form {
            margin-top: auto;
        }

        .key-input {
            width: 100%;
            height: 50px;

            padding: 0 15px;

            color: var(--text);

            background: #0a0908;

            border: 1px solid var(--border-light);

            outline: none;

            font-size: 13px;
            font-weight: 600;

            letter-spacing: 0.04em;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .key-input::placeholder {
            color: #57514c;
        }

        .key-input:focus {
            background: #0d0b0a;
            border-color: var(--orange);
        }

        .primary-button {
            width: 100%;
            height: 50px;

            margin-top: 9px;

            border: 0;

            background: var(--orange);
            color: #0b0908;

            cursor: pointer;

            font-size: 12px;
            font-weight: 900;

            letter-spacing: 0.11em;
            text-transform: uppercase;

            transition:
                background 0.15s ease,
                transform 0.15s ease;
        }

        .primary-button:hover {
            background: var(--orange-light);
        }

        .primary-button:active {
            transform: translateY(1px);
        }

        /* ====================================================
           APPROVED STATE
           ==================================================== */

        .approved-box {
            margin-top: auto;

            padding: 18px;

            border: 1px solid rgba(114, 213, 114, 0.28);

            background: rgba(114, 213, 114, 0.045);
        }

        .approved-title {
            display: flex;
            align-items: center;
            gap: 9px;

            color: var(--success);

            font-size: 12px;
            font-weight: 900;

            letter-spacing: 0.1em;
            text-transform: uppercase;

            margin-bottom: 9px;
        }

        .approved-icon {
            width: 18px;
            height: 18px;

            display: flex;
            align-items: center;
            justify-content: center;

            border: 1px solid var(--success);

            font-size: 10px;
        }

        .approved-text {
            color: var(--text-soft);

            font-size: 12px;
            line-height: 1.5;

            margin-bottom: 15px;
        }

        .download-button {
            display: flex;
            align-items: center;
            justify-content: center;

            width: 100%;
            height: 48px;

            background: var(--orange);
            color: #0b0908;

            font-size: 12px;
            font-weight: 900;

            letter-spacing: 0.11em;
            text-transform: uppercase;

            transition: background 0.15s ease;
        }

        .download-button:hover {
            background: var(--orange-light);
        }

        /* ====================================================
           MESSAGE
           ==================================================== */

        .message {
            margin-bottom: 18px;

            padding: 14px 16px;

            border: 1px solid rgba(255, 73, 73, 0.3);

            background: rgba(255, 73, 73, 0.045);

            color: #ff8585;

            font-size: 12px;
            line-height: 1.5;
        }

        /* ====================================================
           FEATURE GRID
           ==================================================== */

        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);

            gap: 1px;

            background: var(--border);

            border: 1px solid var(--border);

            margin-top: 18px;
        }

        .feature {
            min-height: 170px;

            padding: 24px;

            background: var(--panel);
        }

        .feature-index {
            color: var(--orange);

            font-size: 10px;
            font-weight: 900;

            letter-spacing: 0.12em;

            margin-bottom: 22px;
        }

        .feature h3 {
            font-size: 15px;
            font-weight: 800;

            margin-bottom: 9px;
        }

        .feature p {
            color: var(--text-muted);

            font-size: 12px;
            line-height: 1.6;
        }

        /* ====================================================
           FOOTER
           ==================================================== */

        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;

            margin-top: 18px;

            padding: 19px 3px;

            color: var(--text-muted);

            font-size: 10px;
            font-weight: 700;

            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .footer-links {
            display: flex;
            gap: 20px;
        }

        .footer-link {
            transition: color 0.15s ease;
        }

        .footer-link:hover {
            color: var(--orange);
        }

        /* ====================================================
           WAITING STATUS
           ==================================================== */

        .waiting {
            display: flex;
            align-items: center;
            gap: 9px;

            margin-top: 12px;

            color: var(--text-muted);

            font-size: 10px;
            font-weight: 700;

            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .waiting-dot {
            width: 6px;
            height: 6px;

            background: var(--orange);

            animation: waitingPulse 1.5s ease-in-out infinite;
        }

        @keyframes waitingPulse {
            0%,
            100% {
                opacity: 0.3;
            }

            50% {
                opacity: 1;
            }
        }

        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 800px) {
            .page {
                width: min(100% - 22px, 600px);
                padding-top: 15px;
            }

            .topbar {
                margin-bottom: 24px;
            }

            .brand-version {
                display: none;
            }

            .status {
                font-size: 9px;
            }

            .hero {
                grid-template-columns: 1fr;
            }

            .hero-main {
                min-height: 310px;
                padding: 27px;
            }

            .hero h1 {
                font-size: 50px;
            }

            .access {
                padding: 22px;
                min-height: 310px;
            }

            .features {
                grid-template-columns: 1fr;
            }

            .feature {
                min-height: auto;
            }

            .footer {
                flex-direction: column;
                gap: 14px;
                align-items: flex-start;
            }
        }

        @media (max-width: 420px) {
            .hero h1 {
                font-size: 43px;
            }

            .hero-description {
                font-size: 13px;
            }

            .brand-name {
                font-size: 14px;
            }
        }
    </style>
</head>

<body>

<div class="page">

    <!-- TOP BAR -->

    <header class="topbar">

        <a href="/" class="brand">

            <div class="brand-mark">
                G
            </div>

            <div class="brand-name">
                GENGA
            </div>

            <div class="brand-version">
                1.21.11
            </div>

        </a>

        <div class="status">
            <span class="status-dot"></span>
            ONLINE
        </div>

    </header>


    <!-- MESSAGE -->

    {% if message %}
        <div class="message">
            {{ message }}
        </div>
    {% endif %}


    <!-- HERO -->

    <main>

        <section class="hero">

            <div class="hero-main">

                <div class="eyebrow">
                    GENGA / CLIENT
                </div>

                <h1>
                    GENGA<br>
                    CLIENT
                </h1>

                <p class="hero-description">
                    A clean and lightweight Minecraft client for
                    version 1.21.11. Enter your access key to request
                    a download.
                </p>

                <div class="hero-meta">
                    <span class="meta-line"></span>
                    <span>ACCESS SYSTEM</span>
                    <span>01</span>
                </div>

            </div>


            <!-- ACCESS -->

            <div class="access">

                <div class="panel-heading">

                    <div class="panel-label">
                        Access
                    </div>

                    <div class="panel-number">
                        01
                    </div>

                </div>


                {% if download_ready %}

                    <h2>
                        Access granted
                    </h2>

                    <p class="access-text">
                        Your key has been approved. The GENGA
                        Client download is now available.
                    </p>

                    <div class="approved-box">

                        <div class="approved-title">

                            <span class="approved-icon">
                                ✓
                            </span>

                            APPROVED

                        </div>

                        <p class="approved-text">
                            Your request was approved successfully.
                        </p>

                        <a
                            class="download-button"
                            href="/download/{{ request_id }}"
                        >
                            Download Client
                        </a>

                    </div>

                {% else %}

                    <h2>
                        Enter key
                    </h2>

                    <p class="access-text">
                        Enter your valid GENGA access key below.
                        Your request will be reviewed before the
                        download becomes available.
                    </p>

                    <form
                        class="key-form"
                        action="/request-download"
                        method="POST"
                    >

                        <input
                            class="key-input"
                            type="text"
                            name="key"
                            placeholder="GENGA-XXXX-XXXX"
                            autocomplete="off"
                            spellcheck="false"
                            required
                        >

                        <button
                            class="primary-button"
                            type="submit"
                        >
                            Request Access
                        </button>

                    </form>

                    {% if request_id %}

                        <div class="waiting">

                            <span class="waiting-dot"></span>

                            Waiting for approval

                        </div>

                    {% endif %}

                {% endif %}

            </div>

        </section>


        <!-- FEATURES -->

        <section class="features">

            <article class="feature">

                <div class="feature-index">
                    01 / CLIENT
                </div>

                <h3>
                    Minecraft 1.21.11
                </h3>

                <p>
                    Built specifically around the GENGA Client
                    environment for Minecraft 1.21.11.
                </p>

            </article>


            <article class="feature">

                <div class="feature-index">
                    02 / ACCESS
                </div>

                <h3>
                    Key controlled
                </h3>

                <p>
                    Downloads are protected behind an access-key
                    approval system.
                </p>

            </article>


            <article class="feature">

                <div class="feature-index">
                    03 / COMMUNITY
                </div>

                <h3>
                    GENGA Discord
                </h3>

                <p>
                    Join the GENGA community for updates,
                    announcements and support.
                </p>

            </article>

        </section>

    </main>


    <!-- FOOTER -->

    <footer class="footer">

        <div>
            GENGA CLIENT © 2026
        </div>

        <div class="footer-links">

            <a
                class="footer-link"
                href="{{ discord_url }}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Discord
            </a>

            <a
                class="footer-link"
                href="/admin"
            >
                Admin
            </a>

        </div>

    </footer>

</div>


<!-- ========================================================
     APPROVAL CHECK
     ======================================================== -->

<script>

    const requestId = {{ request_id|tojson }};
    const approvalView = {{ approved_view|tojson }};

    let approvalHandled = false;
    let checking = false;


    async function checkApproval() {

        /*
         * Do absolutely nothing when:
         *
         * 1. There is no request.
         * 2. We are already displaying the approved page.
         * 3. Approval has already been handled.
         * 4. Another request is currently running.
         */

        if (
            !requestId ||
            approvalView ||
            approvalHandled ||
            checking
        ) {
            return;
        }


        checking = true;


        try {

            const response = await fetch(
                "/status/" + encodeURIComponent(requestId),
                {
                    method: "GET",
                    cache: "no-store",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );


            if (response.ok) {

                const data = await response.json();


                if (data.status === "approved") {

                    /*
                     * IMPORTANT:
                     *
                     * Stop checking immediately.
                     *
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
            }

        } catch (error) {

            console.log(
                "Approval check failed:",
                error
            );

        } finally {

            checking = false;
        }


        /*
         * Instead of setInterval(), schedule the next check
         * only after the current request has finished.
         *
         * Once approval is detected, this code never schedules
         * another check.
         */

        if (
            !approvalHandled &&
            !approvalView
        ) {

            setTimeout(
                checkApproval,
                2000
            );
        }
    }


    /*
     * Start checking only when a request exists and
     * we are NOT already on the approved page.
     */

    if (
        requestId &&
        !approvalView
    ) {

        checkApproval();
    }

</script>

</body>
</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    cleanup_old_requests()

    request_id = request.args.get("request", "").strip()

    approved_view = (
        request.args.get("approved") == "1"
    )

    download_ready = False

    if request_id:

        request_data = PENDING_REQUESTS.get(request_id)

        if request_data:

            download_ready = bool(
                request_data.get("approved", False)
            )

    return render_template_string(
        MAIN_HTML,

        request_id=request_id,

        download_ready=download_ready,

        approved_view=approved_view,

        message=request.args.get("message", ""),

        discord_url=DISCORD_URL
    )


# ============================================================
# REQUEST DOWNLOAD
# ============================================================

@app.route("/request-download", methods=["POST"])
def request_download():

    cleanup_old_requests()

    key = request.form.get("key", "").strip()

    if not key:

        return redirect(
            url_for(
                "index",
                message="Please enter an access key."
            )
        )


    # --------------------------------------------------------
    # Validate key
    # --------------------------------------------------------

    if key not in VALID_KEYS:

        return redirect(
            url_for(
                "index",
                message="Invalid access key."
            )
        )


    # --------------------------------------------------------
    # Create request
    # --------------------------------------------------------

    request_id = str(uuid.uuid4())


    PENDING_REQUESTS[request_id] = {

        "key": key,

        "approved": False,

        "created": time.time()

    }


    # --------------------------------------------------------
    # Discord notification
    # --------------------------------------------------------

    if DISCORD_WEBHOOK_URL:

        try:

            payload = {

                "username": "GENGA Access System",

                "embeds": [

                    {

                        "title": "New GENGA Download Request",

                        "description":
                            "A new client download request "
                            "requires approval.",

                        "color": 16731136,

                        "fields": [

                            {
                                "name": "Key",
                                "value": f"`{key}`",
                                "inline": True
                            },

                            {
                                "name": "Request ID",
                                "value": f"`{request_id}`",
                                "inline": True
                            },

                            {
                                "name": "Admin Panel",
                                "value": ADMIN_URL,
                                "inline": False
                            }

                        ]

                    }

                ]

            }


            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=15
            )


            print(
                "Discord Webhook Status:",
                response.status_code
            )


            if not response.ok:

                print(
                    "Discord Webhook Error:",
                    response.text
                )


        except Exception as error:

            print(
                "Discord Webhook Exception:",
                error
            )


    # --------------------------------------------------------
    # Redirect to waiting page
    # --------------------------------------------------------

    return redirect(
        url_for(
            "index",
            request=request_id
        )
    )


# ============================================================
# REQUEST STATUS
# ============================================================

@app.route("/status/<request_id>")
def request_status(request_id):

    request_data = PENDING_REQUESTS.get(request_id)

    if not request_data:

        return jsonify({
            "status": "not_found"
        }), 404


    if request_data.get("approved"):

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

    <meta
        name="theme-color"
        content="#090807"
    >

    <title>GENGA Admin</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;

            margin: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            padding: 20px;

            background: #090807;
            color: #f2eee9;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .card {
            width: 100%;
            max-width: 390px;

            padding: 30px;

            background: #11100e;

            border: 1px solid #292522;
        }

        .brand {
            color: #ff4b00;

            font-size: 11px;
            font-weight: 900;

            letter-spacing: 0.18em;
            text-transform: uppercase;

            margin-bottom: 24px;
        }

        h1 {
            margin: 0 0 9px;

            font-size: 27px;
            font-weight: 850;
        }

        p {
            margin: 0 0 23px;

            color: #706a65;

            font-size: 13px;
            line-height: 1.5;
        }

        input {
            width: 100%;
            height: 50px;

            padding: 0 14px;

            border: 1px solid #37312c;
            outline: none;

            background: #0a0908;
            color: #f2eee9;

            font-size: 13px;
        }

        input:focus {
            border-color: #ff4b00;
        }

        button {
            width: 100%;
            height: 50px;

            margin-top: 9px;

            border: 0;

            background: #ff4b00;
            color: #0b0908;

            cursor: pointer;

            font-size: 11px;
            font-weight: 900;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .error {
            margin-bottom: 14px;

            padding: 12px;

            background: rgba(255, 73, 73, 0.05);

            border: 1px solid rgba(255, 73, 73, 0.25);

            color: #ff8585;

            font-size: 12px;
        }

    </style>

</head>

<body>

    <div class="card">

        <div class="brand">
            GENGA / ADMIN
        </div>

        <h1>
            Admin Login
        </h1>

        <p>
            Sign in to manage client download requests.
        </p>

        {% if error %}

            <div class="error">
                {{ error }}
            </div>

        {% endif %}

        <form
            method="POST"
            action="/admin"
        >

            <input
                type="password"
                name="password"
                placeholder="Admin password"
                autocomplete="current-password"
                required
            >

            <button type="submit">
                Sign in
            </button>

        </form>

    </div>

</body>

</html>
"""


# ============================================================
# ADMIN ROUTE
# ============================================================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if session.get("admin_logged_in"):

        return redirect(
            url_for("admin_panel")
        )


    error = ""


    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if password and password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_panel")
            )


        error = "Invalid admin password."


    return render_template_string(
        ADMIN_LOGIN_HTML,
        error=error
    )


# ============================================================
# ADMIN PANEL
# ============================================================

ADMIN_PANEL_HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#090807"
    >

    <title>GENGA Admin Panel</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;

            margin: 0;

            background: #090807;
            color: #f2eee9;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .page {
            width: min(1050px, calc(100% - 28px));

            margin: 0 auto;

            padding: 25px 0 50px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;

            padding-bottom: 20px;
            margin-bottom: 28px;

            border-bottom: 1px solid #292522;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .mark {
            width: 27px;
            height: 27px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: #ff4b00;
            color: #0a0807;

            font-weight: 900;
            font-size: 12px;
        }

        .brand-text {
            font-size: 14px;
            font-weight: 900;

            letter-spacing: 0.15em;
        }

        .logout {
            color: #706a65;

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .logout:hover {
            color: #ff4b00;
        }

        .heading {
            margin-bottom: 20px;
        }

        .eyebrow {
            color: #ff4b00;

            font-size: 10px;
            font-weight: 900;

            letter-spacing: 0.16em;
            text-transform: uppercase;

            margin-bottom: 9px;
        }

        h1 {
            margin: 0;

            font-size: 32px;
            font-weight: 900;

            letter-spacing: -0.035em;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);

            gap: 1px;

            background: #292522;

            border: 1px solid #292522;

            margin-bottom: 20px;
        }

        .stat {
            padding: 20px;

            background: #11100e;
        }

        .stat-label {
            color: #706a65;

            font-size: 9px;
            font-weight: 800;

            letter-spacing: 0.13em;
            text-transform: uppercase;

            margin-bottom: 9px;
        }

        .stat-value {
            color: #f2eee9;

            font-size: 25px;
            font-weight: 900;
        }

        .requests {
            display: flex;
            flex-direction: column;

            gap: 8px;
        }

        .request {
            padding: 19px;

            background: #11100e;

            border: 1px solid #292522;
        }

        .request-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;

            gap: 15px;

            margin-bottom: 15px;
        }

        .request-id {
            color: #706a65;

            font-size: 9px;
            font-weight: 700;

            letter-spacing: 0.04em;

            word-break: break-all;
        }

        .status {
            padding: 5px 8px;

            border: 1px solid #37312c;

            font-size: 9px;
            font-weight: 900;

            letter-spacing: 0.08em;
            text-transform: uppercase;

            white-space: nowrap;
        }

        .status.pending {
            color: #ff641a;
            border-color: rgba(255, 75, 0, 0.25);
        }

        .status.approved {
            color: #72d572;
            border-color: rgba(114, 213, 114, 0.25);
        }

        .details {
            display: grid;
            grid-template-columns: 1fr 1fr;

            gap: 12px;

            margin-bottom: 15px;
        }

        .detail-label {
            color: #706a65;

            font-size: 9px;
            font-weight: 800;

            letter-spacing: 0.1em;
            text-transform: uppercase;

            margin-bottom: 5px;
        }

        .detail-value {
            color: #d7d1cb;

            font-size: 12px;

            word-break: break-all;
        }

        .approve {
            display: inline-flex;
            align-items: center;
            justify-content: center;

            height: 39px;

            padding: 0 16px;

            border: 0;

            background: #ff4b00;
            color: #0b0908;

            font-size: 10px;
            font-weight: 900;

            letter-spacing: 0.08em;
            text-transform: uppercase;

            cursor: pointer;
        }

        .approve:hover {
            background: #ff641a;
        }

        .empty {
            padding: 45px 20px;

            text-align: center;

            background: #11100e;

            border: 1px solid #292522;

            color: #706a65;

            font-size: 12px;
        }

        @media (max-width: 650px) {

            .stats {
                grid-template-columns: 1fr;
            }

            .details {
                grid-template-columns: 1fr;
            }

            .request-top {
                flex-direction: column;
            }

        }

    </style>

</head>

<body>

<div class="page">

    <header class="topbar">

        <div class="brand">

            <div class="mark">
                G
            </div>

            <div class="brand-text">
                GENGA ADMIN
            </div>

        </div>

        <a
            class="logout"
            href="/admin/logout"
        >
            Logout
        </a>

    </header>


    <div class="heading">

        <div class="eyebrow">
            Access management
        </div>

        <h1>
            Download Requests
        </h1>

    </div>


    <section class="stats">

        <div class="stat">

            <div class="stat-label">
                Total
            </div>

            <div class="stat-value">
                {{ total }}
            </div>

        </div>


        <div class="stat">

            <div class="stat-label">
                Pending
            </div>

            <div class="stat-value">
                {{ pending }}
            </div>

        </div>


        <div class="stat">

            <div class="stat-label">
                Approved
            </div>

            <div class="stat-value">
                {{ approved }}
            </div>

        </div>

    </section>


    <section class="requests">

        {% if requests %}

            {% for request_id, data in requests %}

                <article class="request">

                    <div class="request-top">

                        <div class="request-id">
                            {{ request_id }}
                        </div>

                        {% if data.approved %}

                            <div class="status approved">
                                Approved
                            </div>

                        {% else %}

                            <div class="status pending">
                                Pending
                            </div>

                        {% endif %}

                    </div>


                    <div class="details">

                        <div>

                            <div class="detail-label">
                                Access Key
                            </div>

                            <div class="detail-value">
                                {{ data.key }}
                            </div>

                        </div>


                        <div>

                            <div class="detail-label">
                                Created
                            </div>

                            <div class="detail-value">
                                {{ data.created_text }}
                            </div>

                        </div>

                    </div>


                    {% if not data.approved %}

                        <form
                            method="POST"
                            action="/admin/approve/{{ request_id }}"
                        >

                            <button
                                class="approve"
                                type="submit"
                            >
                                Approve Request
                            </button>

                        </form>

                    {% endif %}

                </article>

            {% endfor %}

        {% else %}

            <div class="empty">
                No download requests yet.
            </div>

        {% endif %}

    </section>

</div>

</body>

</html>
"""


@app.route("/admin/panel")
@admin_required
def admin_panel():

    cleanup_old_requests()

    request_items = []

    for request_id, data in PENDING_REQUESTS.items():

        request_copy = dict(data)

        request_copy["created_text"] = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                data.get("created", time.time())
            )
        )

        request_items.append(
            (
                request_id,
                request_copy
            )
        )


    request_items.sort(
        key=lambda item: item[1].get(
            "created",
            0
        ),
        reverse=True
    )


    total = len(request_items)

    pending = sum(
        1
        for _, data in request_items
        if not data.get("approved")
    )

    approved = sum(
        1
        for _, data in request_items
        if data.get("approved")
    )


    return render_template_string(

        ADMIN_PANEL_HTML,

        requests=request_items,

        total=total,

        pending=pending,

        approved=approved
    )


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


    if not request_data:

        return redirect(
            url_for("admin_panel")
        )


    request_data["approved"] = True

    request_data["approved_at"] = time.time()


    print(
        f"GENGA request approved: {request_id}"
    )


    return redirect(
        url_for("admin_panel")
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route("/download/<request_id>")
def download(request_id):

    request_data = PENDING_REQUESTS.get(
        request_id
    )


    if not request_data:

        return (
            "Download request not found.",
            404
        )


    if not request_data.get("approved"):

        return (
            "This download request has not been approved.",
            403
        )


    if not os.path.isfile(DOWNLOAD_PATH):

        print(
            "Download file not found:",
            DOWNLOAD_PATH
        )

        return (
            "Download file is currently unavailable.",
            404
        )


    return send_file(
        DOWNLOAD_PATH,
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
# START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
