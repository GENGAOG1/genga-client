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
# GENGA CLIENT WEBSITE
# ============================================================

app = Flask(__name__)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

app.secret_key = os.environ.get("GENGA_SECRET_KEY", "change-this-secret-key")

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

GENGA_VALID_KEYS = [
    key.strip()
    for key in os.environ.get("GENGA_VALID_KEYS", "").split(",")
    if key.strip()
]

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

# IMPORTANT:
# Replace this with your real Discord invite if necessary.
DISCORD_URL = "https://discord.gg/VEEV2gaeB"

ADMIN_URL = "https://genga-client.onrender.com/admin"


# ------------------------------------------------------------
# Temporary download requests
# ------------------------------------------------------------
#
# Structure:
#
# {
#     request_id: {
#         "key": "...",
#         "approved": False,
#         "created": 1234567890
#     }
# }
#
# NOTE:
# This is stored in RAM.
# A Render restart clears this dictionary.
#

PENDING_REQUESTS = {}


# ============================================================
# ADMIN AUTH
# ============================================================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))

        return func(*args, **kwargs)

    return wrapper


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

    <meta
        name="theme-color"
        content="#080706"
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
                    circle at 15% 10%,
                    rgba(255, 65, 0, 0.08),
                    transparent 32%
                ),
                radial-gradient(
                    circle at 85% 90%,
                    rgba(255, 95, 0, 0.05),
                    transparent 30%
                ),
                #080706;

            color: #f1efed;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
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
           APP SHELL
           ==================================================== */

        .page {
            width: 100%;
            min-height: 100vh;
            padding: 28px 18px 50px;
        }

        .app-shell {
            width: 100%;
            max-width: 1120px;
            margin: 0 auto;

            border: 1px solid #292521;
            background: #0d0c0b;

            box-shadow:
                0 25px 80px rgba(0, 0, 0, 0.45);
        }

        /* ====================================================
           TOP BAR
           ==================================================== */

        .topbar {
            min-height: 68px;

            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 0 24px;

            border-bottom: 1px solid #292521;
            background: #0b0a09;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-mark {
            width: 11px;
            height: 28px;

            background: #ff4b00;

            transform: skewX(-18deg);
        }

        .brand-name {
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 0.16em;
        }

        .brand-version {
            color: #77716b;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;

            color: #8d8781;

            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #ff4b00;
            box-shadow: 0 0 10px rgba(255, 75, 0, 0.4);
        }

        /* ====================================================
           HERO
           ==================================================== */

        .hero {
            padding: 58px 48px 44px;

            border-bottom: 1px solid #292521;

            position: relative;
            overflow: hidden;
        }

        .hero::after {
            content: "";

            position: absolute;
            right: -100px;
            top: 40px;

            width: 280px;
            height: 280px;

            border: 1px solid rgba(255, 75, 0, 0.07);

            transform: rotate(45deg);
            pointer-events: none;
        }

        .eyebrow {
            color: #ff5a0a;

            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.18em;
            text-transform: uppercase;

            margin-bottom: 15px;
        }

        .hero h1 {
            margin: 0;

            font-size: clamp(42px, 7vw, 76px);
            line-height: 0.95;

            font-weight: 900;
            letter-spacing: -0.055em;
        }

        .hero h1 span {
            color: #ff4b00;
        }

        .hero-description {
            max-width: 610px;

            margin-top: 22px;

            color: #8c857f;

            font-size: 15px;
            line-height: 1.7;
        }

        .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            margin-top: 28px;
        }

        .meta-item {
            border: 1px solid #2c2723;
            background: #11100e;

            padding: 8px 11px;

            color: #77716b;

            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .meta-item strong {
            color: #d8d3cf;
        }

        /* ====================================================
           MAIN GRID
           ==================================================== */

        .main-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.4fr) minmax(310px, 0.8fr);
        }

        /* ====================================================
           CONTENT
           ==================================================== */

        .content {
            padding: 36px 40px;
            border-right: 1px solid #292521;
        }

        .section-label {
            margin-bottom: 18px;

            color: #77716b;

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        /* ====================================================
           FEATURES
           ==================================================== */

        .features {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }

        .feature {
            min-height: 125px;

            padding: 18px;

            border: 1px solid #292521;
            background: #11100e;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .feature:hover {
            border-color: #493229;
            background: #141210;
        }

        .feature-number {
            color: #ff4b00;

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.1em;
        }

        .feature-title {
            margin-top: 18px;

            font-size: 14px;
            font-weight: 800;
        }

        .feature-description {
            margin-top: 7px;

            color: #77716b;

            font-size: 12px;
            line-height: 1.5;
        }

        /* ====================================================
           ACCESS PANEL
           ==================================================== */

        .access-panel {
            padding: 36px 30px;

            background: #0a0908;
        }

        .access-title {
            margin: 0;

            font-size: 22px;
            font-weight: 850;
            letter-spacing: -0.02em;
        }

        .access-description {
            margin: 10px 0 24px;

            color: #77716b;

            font-size: 12px;
            line-height: 1.6;
        }

        .key-form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .key-input {
            width: 100%;

            border: 1px solid #302a26;
            outline: none;

            background: #11100e;

            color: #f1efed;

            padding: 14px 15px;

            font-size: 13px;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .key-input::placeholder {
            color: #55504b;
        }

        .key-input:focus {
            border-color: #ff4b00;
            background: #141210;
        }

        .button {
            width: 100%;

            border: 0;

            padding: 14px 16px;

            background: #ff4b00;
            color: #080706;

            cursor: pointer;

            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;

            transition:
                background 0.15s ease,
                transform 0.1s ease;
        }

        .button:hover {
            background: #ff5c16;
        }

        .button:active {
            transform: translateY(1px);
        }

        .button.secondary {
            margin-top: 10px;

            border: 1px solid #302a26;

            background: transparent;
            color: #d5d0cc;
        }

        .button.secondary:hover {
            border-color: #ff4b00;
            background: #15110e;
        }

        /* ====================================================
           APPROVED
           ==================================================== */

        .approved {
            border: 1px solid #4a2b1d;
            background: #120d09;

            padding: 18px;
        }

        .approved-top {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .approved-icon {
            width: 24px;
            height: 24px;

            display: grid;
            place-items: center;

            background: #ff4b00;
            color: #080706;

            font-size: 13px;
            font-weight: 900;
        }

        .approved-title {
            color: #ff6a22;

            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .approved-text {
            margin-top: 14px;

            color: #918983;

            font-size: 12px;
            line-height: 1.6;
        }

        /* ====================================================
           WAITING
           ==================================================== */

        .waiting {
            border: 1px solid #302a26;
            background: #11100e;

            padding: 17px;
        }

        .waiting-header {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .waiting-dot {
            width: 8px;
            height: 8px;

            border-radius: 50%;

            background: #ff4b00;
        }

        .waiting-title {
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .waiting-text {
            margin-top: 10px;

            color: #77716b;

            font-size: 11px;
            line-height: 1.55;
        }

        /* ====================================================
           MESSAGE
           ==================================================== */

        .message {
            margin-bottom: 15px;

            padding: 12px 14px;

            border-left: 3px solid #ff4b00;

            background: #15110e;

            color: #aaa39d;

            font-size: 12px;
            line-height: 1.5;
        }

        /* ====================================================
           DISCORD
           ==================================================== */

        .discord {
            margin-top: 30px;

            border: 1px solid #292521;
            background: #11100e;

            padding: 20px;
        }

        .discord-label {
            color: #ff5a0a;

            font-size: 10px;
            font-weight: 900;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .discord-title {
            margin-top: 8px;

            font-size: 16px;
            font-weight: 800;
        }

        .discord-text {
            margin-top: 7px;

            color: #77716b;

            font-size: 12px;
            line-height: 1.55;
        }

        .discord-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;

            margin-top: 15px;

            border: 1px solid #3a302a;

            padding: 11px 14px;

            background: #151210;
            color: #e5e0dc;

            font-size: 10px;
            font-weight: 900;
            letter-spacing: 0.1em;
            text-transform: uppercase;

            transition:
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .discord-button:hover {
            border-color: #ff4b00;
            background: #1a120e;
        }

        /* ====================================================
           FOOTER
           ==================================================== */

        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;

            padding: 18px 24px;

            border-top: 1px solid #292521;

            color: #57514c;

            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .footer a {
            color: #77716b;
        }

        .footer a:hover {
            color: #ff5a0a;
        }

        /* ====================================================
           RESPONSIVE
           ==================================================== */

        @media (max-width: 800px) {

            .page {
                padding: 12px;
            }

            .topbar {
                padding: 0 17px;
            }

            .hero {
                padding: 42px 25px 34px;
            }

            .main-grid {
                grid-template-columns: 1fr;
            }

            .content {
                border-right: 0;
                border-bottom: 1px solid #292521;
                padding: 28px 20px;
            }

            .access-panel {
                padding: 28px 20px;
            }

            .features {
                grid-template-columns: 1fr;
            }

            .footer {
                flex-direction: column;
                align-items: flex-start;
            }
        }

        @media (max-width: 500px) {

            .brand-version {
                display: none;
            }

            .hero h1 {
                font-size: 48px;
            }

            .hero-description {
                font-size: 13px;
            }
        }

    </style>

</head>

<body>

<div class="page">

    <main class="app-shell">

        <!-- ==================================================
             TOP BAR
             ================================================== -->

        <header class="topbar">

            <a href="/" class="brand">

                <span class="brand-mark"></span>

                <span class="brand-name">
                    GENGA
                </span>

                <span class="brand-version">
                    CLIENT / 1.21.11
                </span>

            </a>

            <div class="status">

                <span class="status-dot"></span>

                SYSTEM ONLINE

            </div>

        </header>


        <!-- ==================================================
             HERO
             ================================================== -->

        <section class="hero">

            <div class="eyebrow">
                Minecraft Client
            </div>

            <h1>
                GENGA <span>CLIENT</span>
            </h1>

            <p class="hero-description">
                A clean, lightweight client experience for Minecraft
                1.21.11. Enter your access key to request your download.
            </p>

            <div class="hero-meta">

                <div class="meta-item">
                    Version <strong>1.21.11</strong>
                </div>

                <div class="meta-item">
                    Loader <strong>Fabric</strong>
                </div>

                <div class="meta-item">
                    Access <strong>Key Required</strong>
                </div>

            </div>

        </section>


        <!-- ==================================================
             MAIN CONTENT
             ================================================== -->

        <div class="main-grid">


            <!-- ==================================================
                 FEATURES
                 ================================================== -->

            <section class="content">

                <div class="section-label">
                    Client Overview
                </div>

                <div class="features">

                    <article class="feature">

                        <div class="feature-number">
                            01
                        </div>

                        <div class="feature-title">
                            Clean Interface
                        </div>

                        <div class="feature-description">
                            Minimal dark interface inspired by the
                            GENGA client GUI.
                        </div>

                    </article>


                    <article class="feature">

                        <div class="feature-number">
                            02
                        </div>

                        <div class="feature-title">
                            Lightweight
                        </div>

                        <div class="feature-description">
                            Designed around a compact client architecture
                            without unnecessary visual elements.
                        </div>

                    </article>


                    <article class="feature">

                        <div class="feature-number">
                            03
                        </div>

                        <div class="feature-title">
                            HUD System
                        </div>

                        <div class="feature-description">
                            Modular HUD elements and configurable client
                            components.
                        </div>

                    </article>


                    <article class="feature">

                        <div class="feature-number">
                            04
                        </div>

                        <div class="feature-title">
                            Minecraft 1.21.11
                        </div>

                        <div class="feature-description">
                            Built specifically around the current GENGA
                            1.21.11 project.
                        </div>

                    </article>

                </div>


                <!-- ==================================================
                     DISCORD
                     ================================================== -->

                <div class="discord">

                    <div class="discord-label">
                        Community
                    </div>

                    <div class="discord-title">
                        Join the GENGA Discord
                    </div>

                    <div class="discord-text">
                        Get updates, announcements, support and information
                        about new GENGA Client releases.
                    </div>

                    <!-- THIS LINK REMAINS ACTIVE -->
                    <a
                        class="discord-button"
                        href="{{ discord_url }}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Join Discord
                    </a>

                </div>

            </section>


            <!-- ==================================================
                 ACCESS
                 ================================================== -->

            <aside class="access-panel">

                <div class="section-label">
                    Client Access
                </div>

                <h2 class="access-title">
                    Download Access
                </h2>

                <p class="access-description">
                    Enter your valid GENGA access key. Your request will
                    be sent to the administration system for approval.
                </p>


                {% if message %}

                    <div class="message">
                        {{ message }}
                    </div>

                {% endif %}


                {% if download_ready %}

                    <!-- ==================================================
                         APPROVED STATE
                         ================================================== -->

                    <div class="approved">

                        <div class="approved-top">

                            <div class="approved-icon">
                                ✓
                            </div>

                            <div class="approved-title">
                                Access Granted
                            </div>

                        </div>

                        <div class="approved-text">
                            Your key has been approved. The GENGA Client
                            download is now available.
                        </div>

                    </div>

                    <a
                        class="button"
                        href="{{ url_for('download', request_id=request_id) }}"
                        style="
                            display:block;
                            text-align:center;
                            margin-top:10px;
                        "
                    >
                        Download GENGA Client
                    </a>


                {% elif request_id %}

                    <!-- ==================================================
                         WAITING STATE
                         ================================================== -->

                    <div class="waiting">

                        <div class="waiting-header">

                            <span class="waiting-dot"></span>

                            <span class="waiting-title">
                                Waiting for approval
                            </span>

                        </div>

                        <div class="waiting-text">
                            Your request has been submitted. Keep this
                            page open while the request is being reviewed.
                        </div>

                    </div>


                {% else %}

                    <!-- ==================================================
                         KEY FORM
                         ================================================== -->

                    <form
                        class="key-form"
                        method="POST"
                        action="{{ url_for('request_download') }}"
                    >

                        <input
                            class="key-input"
                            type="text"
                            name="key"
                            placeholder="Enter access key"
                            autocomplete="off"
                            required
                        >

                        <button
                            class="button"
                            type="submit"
                        >
                            Request Download
                        </button>

                    </form>

                {% endif %}


                <!-- Discord remains available in the access panel too -->

                <a
                    class="button secondary"
                    href="{{ discord_url }}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Open Discord
                </a>

            </aside>

        </div>


        <!-- ==================================================
             FOOTER
             ================================================== -->

        <footer class="footer">

            <span>
                GENGA CLIENT
            </span>

            <span>
                Minecraft 1.21.11
            </span>

            <a
                href="{{ discord_url }}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Discord
            </a>

        </footer>

    </main>

</div>


<!-- ==========================================================
     APPROVAL CHECK
     ========================================================== -->

<script>

    const requestId = {{ request_id|tojson }};

    /*
     * approved_view becomes true after the ONE navigation
     * that happens when the admin approves the request.
     *
     * On that page we DO NOT start polling again.
     */

    const approvedView = {{ approved_view|tojson }};

    let approvalHandled = false;


    async function checkStatus() {

        /*
         * Never do another check after approval.
         */
        if (!requestId || approvedView || approvalHandled) {
            return;
        }


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


            if (!response.ok) {

                /*
                 * Request may have disappeared after a server restart.
                 * Just try again later.
                 */

                scheduleNextCheck();

                return;
            }


            const data = await response.json();


            if (data.status === "approved") {

                /*
                 * IMPORTANT:
                 *
                 * Stop the polling completely.
                 *
                 * Then perform exactly ONE navigation to the
                 * approved page.
                 */

                approvalHandled = true;

                window.location.replace(
                    "/?request=" +
                    encodeURIComponent(requestId) +
                    "&approved=1"
                );

                return;
            }


            /*
             * Still pending.
             */
            scheduleNextCheck();

        } catch (error) {

            /*
             * Network error:
             * retry later.
             */

            scheduleNextCheck();
        }
    }


    function scheduleNextCheck() {

        if (!approvalHandled && !approvedView) {

            setTimeout(checkStatus, 2000);

        }
    }


    /*
     * Only start polling when we are actually waiting
     * for an approval.
     */

    if (requestId && !approvedView) {

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

    request_id = request.args.get("request")

    approved_view = request.args.get("approved") == "1"

    message = request.args.get("message")

    download_ready = False


    if request_id:

        request_data = PENDING_REQUESTS.get(request_id)

        if request_data:

            if request_data.get("approved"):

                download_ready = True


    return render_template_string(
        HTML,

        request_id=request_id,
        approved_view=approved_view,
        download_ready=download_ready,
        message=message,
        discord_url=DISCORD_URL
    )


# ============================================================
# REQUEST DOWNLOAD
# ============================================================

@app.route("/request-download", methods=["POST"])
def request_download():

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

    if key not in GENGA_VALID_KEYS:

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
    # Discord webhook
    # --------------------------------------------------------

    if DISCORD_WEBHOOK_URL:

        webhook_payload = {

            "content": (
                "## GENGA Client — Download Request\n\n"
                f"**Key:** `{key}`\n"
                f"**Request ID:** `{request_id}`\n\n"
                f"**Approve:** {ADMIN_URL}/admin/panel"
            )

        }


        try:

            requests.post(
                DISCORD_WEBHOOK_URL,
                json=webhook_payload,
                timeout=10
            )

        except requests.RequestException as error:

            print(
                "Discord webhook error:",
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
# STATUS
# ============================================================

@app.route("/status/<request_id>", methods=["GET"])
def status(request_id):

    request_data = PENDING_REQUESTS.get(request_id)


    if not request_data:

        return jsonify(
            {
                "status": "not_found"
            }
        ), 404


    if request_data.get("approved"):

        return jsonify(
            {
                "status": "approved"
            }
        )


    return jsonify(
        {
            "status": "pending"
        }
    )


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

            padding: 20px;

            background: #080706;
            color: #f0ece8;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
        }

        .panel {
            width: 100%;
            max-width: 420px;

            border: 1px solid #292521;

            background: #0d0c0b;

            padding: 30px;

            box-shadow:
                0 25px 80px rgba(0, 0, 0, 0.5);
        }

        .mark {
            width: 10px;
            height: 27px;

            background: #ff4b00;

            transform: skewX(-18deg);

            margin-bottom: 20px;
        }

        h1 {
            margin: 0;

            font-size: 25px;
            font-weight: 900;
        }

        p {
            color: #77716b;

            font-size: 12px;
            line-height: 1.6;
        }

        input {
            width: 100%;

            margin-top: 12px;

            padding: 14px;

            border: 1px solid #302a26;
            outline: none;

            background: #11100e;
            color: #fff;
        }

        input:focus {
            border-color: #ff4b00;
        }

        button {
            width: 100%;

            margin-top: 10px;

            padding: 14px;

            border: 0;

            background: #ff4b00;
            color: #080706;

            cursor: pointer;

            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .error {
            margin-top: 15px;

            padding: 12px;

            border-left: 3px solid #ff4b00;

            background: #15110e;

            color: #a69e97;

            font-size: 12px;
        }

    </style>

</head>

<body>

    <div class="panel">

        <div class="mark"></div>

        <h1>GENGA ADMIN</h1>

        <p>
            Administrative access required.
        </p>

        <form method="POST">

            <input
                type="password"
                name="password"
                placeholder="Admin password"
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

        password = request.form.get(
            "password",
            ""
        )


        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_panel")
            )


        return render_template_string(
            ADMIN_LOGIN_HTML,
            error="Invalid admin password."
        )


    return render_template_string(
        ADMIN_LOGIN_HTML,
        error=None
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

    <title>GENGA Admin Panel</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;

            background: #080706;
            color: #f0ece8;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
        }

        .page {
            width: 100%;
            max-width: 1050px;

            margin: 0 auto;

            padding: 30px 18px 60px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;

            gap: 20px;

            padding-bottom: 22px;

            border-bottom: 1px solid #292521;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .mark {
            width: 9px;
            height: 25px;

            background: #ff4b00;

            transform: skewX(-18deg);
        }

        h1 {
            margin: 0;

            font-size: 23px;
            font-weight: 900;
        }

        .logout {
            color: #77716b;

            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .logout:hover {
            color: #ff4b00;
        }

        .request {
            margin-top: 12px;

            border: 1px solid #292521;

            background: #0d0c0b;

            padding: 18px;
        }

        .request.pending {
            border-left: 3px solid #ff4b00;
        }

        .request.approved {
            border-left: 3px solid #67513f;
        }

        .request-top {
            display: flex;
            align-items: center;
            justify-content: space-between;

            gap: 20px;
        }

        .request-id {
            color: #ff6a22;

            font-family: monospace;
            font-size: 12px;

            word-break: break-all;
        }

        .badge {
            padding: 6px 9px;

            background: #171310;

            color: #ff7b3c;

            font-size: 9px;
            font-weight: 900;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .info {
            margin-top: 13px;

            color: #77716b;

            font-family: monospace;
            font-size: 11px;

            line-height: 1.7;
        }

        .approve {
            display: inline-block;

            margin-top: 14px;

            border: 0;

            padding: 10px 13px;

            background: #ff4b00;
            color: #080706;

            cursor: pointer;

            font-size: 10px;
            font-weight: 900;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .approve:hover {
            background: #ff5c16;
        }

        .empty {
            margin-top: 30px;

            padding: 30px;

            border: 1px solid #292521;

            color: #77716b;

            text-align: center;

            font-size: 12px;
        }

    </style>

</head>

<body>

<div class="page">

    <header class="header">

        <div class="brand">

            <div class="mark"></div>

            <h1>
                GENGA ADMIN
            </h1>

        </div>

        <a
            class="logout"
            href="{{ url_for('admin_logout') }}"
        >
            Logout
        </a>

    </header>


    {% if requests %}

        {% for request_id, data in requests %}

            <div
                class="request
                {% if data.approved %}
                    approved
                {% else %}
                    pending
                {% endif %}"
            >

                <div class="request-top">

                    <div class="request-id">
                        {{ request_id }}
                    </div>

                    <div class="badge">

                        {% if data.approved %}
                            Approved
                        {% else %}
                            Pending
                        {% endif %}

                    </div>

                </div>


                <div class="info">

                    KEY:
                    {{ data.key }}

                    <br>

                    CREATED:
                    {{ data.created }}

                </div>


                {% if not data.approved %}

                    <form
                        method="POST"
                        action="{{ url_for(
                            'approve_request',
                            request_id=request_id
                        ) }}"
                    >

                        <button
                            class="approve"
                            type="submit"
                        >
                            Approve Request
                        </button>

                    </form>

                {% endif %}

            </div>

        {% endfor %}

    {% else %}

        <div class="empty">
            No download requests.
        </div>

    {% endif %}

</div>

</body>

</html>
"""


@app.route("/admin/panel", methods=["GET"])
@admin_required
def admin_panel():

    requests_list = list(
        PENDING_REQUESTS.items()
    )

    # Newest requests first
    requests_list.reverse()


    return render_template_string(
        ADMIN_PANEL_HTML,
        requests=requests_list
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

@app.route(
    "/download/<request_id>",
    methods=["GET"]
)
def download(request_id):

    request_data = PENDING_REQUESTS.get(request_id)


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


    file_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        DOWNLOAD_DATEI
    )


    if not os.path.isfile(file_path):

        return (
            "Download file is currently unavailable.",
            404
        )


    return send_file(
        file_path,
        as_attachment=True,
        download_name=DOWNLOAD_DATEI
    )


# ============================================================
# CLEAN OLD REQUESTS
# ============================================================

def cleanup_old_requests():

    current_time = time.time()

    expired = []


    for request_id, data in PENDING_REQUESTS.items():

        created = data.get(
            "created",
            current_time
        )


        # Remove requests older than 24 hours.
        if current_time - created > 86400:

            expired.append(request_id)


    for request_id in expired:

        PENDING_REQUESTS.pop(
            request_id,
            None
        )


# ============================================================
# BEFORE REQUEST
# ============================================================

@app.before_request
def before_request():

    cleanup_old_requests()


# ============================================================
# START SERVER
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
        port=port,
        debug=False
    )
