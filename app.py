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

app = Flask(__name__)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

# Diese Werte NICHT in den Code schreiben.
# In Render -> Environment eintragen.

app.secret_key = os.environ.get("GENGA_SECRET_KEY", "")

DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    ""
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    ""
)

# Beispiel:
# GENGA_VALID_KEYS=GENGA-123,GENGA-456,GENGA-789

VALID_KEYS = [
    key.strip()
    for key in os.environ.get(
        "GENGA_VALID_KEYS",
        ""
    ).split(",")
    if key.strip()
]

# ============================================================
# KONFIGURATION
# ============================================================

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

DISCORD_URL = "https://discord.gg/VEEV2gaeB"

# Anfragen werden hier gespeichert.
# Hinweis: Nach einem Render-Neustart sind sie weg.
PENDING_REQUESTS = {}


# ============================================================
# ADMIN LOGIN CHECK
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_authenticated"):
            return redirect(
                url_for("admin_login")
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# HTML
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Genga Client</title>

<style>

/* ============================================================
   RESET
   ============================================================ */

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
}

/* ============================================================
   BODY
   ============================================================ */

body {
    min-height: 100vh;
    overflow-x: hidden;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    color: #ffffff;

    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(124, 58, 237, 0.22),
            transparent 30%
        ),

        radial-gradient(
            circle at 85% 80%,
            rgba(14, 165, 233, 0.16),
            transparent 30%
        ),

        #050507;
}

/* ============================================================
   BACKGROUND
   ============================================================ */

.background {
    position: fixed;
    inset: 0;

    overflow: hidden;

    pointer-events: none;

    z-index: 0;
}

.grid {
    position: absolute;
    inset: -50%;

    background-image:
        linear-gradient(
            rgba(255,255,255,0.035) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(255,255,255,0.035) 1px,
            transparent 1px
        );

    background-size: 55px 55px;

    transform:
        perspective(500px)
        rotateX(55deg);

    animation:
        gridMove 15s linear infinite;
}

@keyframes gridMove {

    from {
        transform:
            perspective(500px)
            rotateX(55deg)
            translateY(0);
    }

    to {
        transform:
            perspective(500px)
            rotateX(55deg)
            translateY(55px);
    }
}

.glow {
    position: absolute;

    width: 350px;
    height: 350px;

    border-radius: 50%;

    filter: blur(110px);

    opacity: 0.25;
}

.glow-one {
    top: -150px;
    left: -100px;

    background: #7c3aed;
}

.glow-two {
    right: -150px;
    bottom: -150px;

    background: #06b6d4;
}

/* ============================================================
   HEADER
   ============================================================ */

header {
    position: relative;
    z-index: 10;

    max-width: 1200px;

    margin: auto;

    padding:
        28px 30px;

    display: flex;

    align-items: center;

    justify-content: space-between;
}

.logo {
    font-size: 23px;

    font-weight: 900;

    letter-spacing: 5px;
}

.logo span {
    color: #8b5cf6;
}

.status {
    display: flex;

    align-items: center;

    gap: 9px;

    padding:
        9px 15px;

    border:
        1px solid
        rgba(255,255,255,0.1);

    border-radius: 999px;

    background:
        rgba(255,255,255,0.04);

    backdrop-filter:
        blur(15px);

    color: #999;

    font-size: 12px;

    letter-spacing: 1px;
}

.status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #4ade80;

    box-shadow:
        0 0 8px #4ade80,
        0 0 18px rgba(74,222,128,0.5);

    animation:
        pulse 2s infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.4;
    }
}

/* ============================================================
   MAIN
   ============================================================ */

main {
    position: relative;

    z-index: 5;

    min-height:
        calc(100vh - 90px);

    display: flex;

    justify-content: center;

    align-items: center;

    padding:
        70px 20px 100px;
}

.hero {
    width: 100%;

    max-width: 950px;

    text-align: center;
}

.badge {
    display: inline-flex;

    align-items: center;

    margin-bottom: 28px;

    padding:
        9px 16px;

    border:
        1px solid
        rgba(139,92,246,0.35);

    border-radius: 999px;

    background:
        rgba(139,92,246,0.08);

    color: #c4b5fd;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 2px;

    text-transform: uppercase;
}

h1 {
    font-size:
        clamp(55px, 10vw, 115px);

    line-height: 0.88;

    font-weight: 950;

    letter-spacing: -7px;

    margin-bottom: 32px;

    background:
        linear-gradient(
            110deg,
            #ffffff 20%,
            #c4b5fd 50%,
            #67e8f9 85%
        );

    -webkit-background-clip: text;

    background-clip: text;

    color: transparent;

    filter:
        drop-shadow(
            0 0 35px
            rgba(124,58,237,0.22)
        );
}

.subtitle {
    max-width: 650px;

    margin: auto;

    color: #92929e;

    font-size: 17px;

    line-height: 1.7;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.buttons {
    display: flex;

    justify-content: center;

    align-items: center;

    gap: 14px;

    margin-top: 40px;

    flex-wrap: wrap;
}

.button {
    position: relative;

    min-width: 200px;

    padding:
        16px 25px;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    border-radius: 13px;

    text-decoration: none;

    font-size: 14px;

    font-weight: 800;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease;
}

.primary {
    color: white;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );

    border:
        1px solid
        rgba(255,255,255,0.12);

    box-shadow:
        0 12px 40px
        rgba(99,67,220,0.35),

        inset 0 1px
        rgba(255,255,255,0.25);
}

.primary:hover {
    transform:
        translateY(-4px);

    box-shadow:
        0 18px 50px
        rgba(99,67,220,0.5),

        inset 0 1px
        rgba(255,255,255,0.3);
}

.secondary {
    color: #dddddf;

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid
        rgba(255,255,255,0.1);

    backdrop-filter:
        blur(15px);
}

.secondary:hover {
    transform:
        translateY(-4px);

    border-color:
        rgba(255,255,255,0.25);

    background:
        rgba(255,255,255,0.07);
}

/* ============================================================
   KEY BOX
   ============================================================ */

.key-box {
    max-width: 500px;

    margin: 30px auto 0;

    padding: 25px;

    border:
        1px solid
        rgba(139,92,246,0.25);

    border-radius: 17px;

    background:
        rgba(255,255,255,0.035);

    backdrop-filter:
        blur(18px);
}

.key-box h2 {
    font-size: 18px;

    margin-bottom: 8px;
}

.key-box p {
    color: #858592;

    font-size: 13px;

    line-height: 1.6;

    margin-bottom: 18px;
}

.key-input {
    width: 100%;

    padding:
        14px 16px;

    border-radius: 10px;

    border:
        1px solid
        rgba(255,255,255,0.12);

    outline: none;

    background:
        rgba(0,0,0,0.35);

    color: white;

    font-size: 14px;

    margin-bottom: 12px;
}

.key-input:focus {
    border-color:
        #8b5cf6;
}

.key-submit {
    width: 100%;

    padding: 14px;

    border: none;

    border-radius: 10px;

    color: white;

    font-weight: 800;

    cursor: pointer;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );
}

.message {
    max-width: 500px;

    margin:
        25px auto 0;

    padding: 14px;

    border-radius: 10px;

    background:
        rgba(255,255,255,0.05);

    color: #aaa;

    font-size: 13px;
}

/* ============================================================
   FEATURES
   ============================================================ */

.features {
    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 15px;

    max-width: 850px;

    margin:
        75px auto 0;
}

.card {
    padding: 25px;

    text-align: left;

    border:
        1px solid
        rgba(255,255,255,0.08);

    border-radius: 17px;

    background:
        rgba(255,255,255,0.035);

    backdrop-filter:
        blur(18px);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease;
}

.card:hover {
    transform:
        translateY(-6px);

    border-color:
        rgba(139,92,246,0.3);
}

.icon {
    width: 42px;
    height: 42px;

    display: flex;

    align-items: center;

    justify-content: center;

    margin-bottom: 17px;

    border-radius: 12px;

    background:
        rgba(139,92,246,0.1);

    border:
        1px solid
        rgba(139,92,246,0.18);

    font-size: 20px;
}

.card h3 {
    margin-bottom: 8px;

    font-size: 15px;
}

.card p {
    color: #80808c;

    font-size: 13px;

    line-height: 1.6;
}

/* ============================================================
   DISCORD
   ============================================================ */

.discord-icon {
    color: #5865F2;

    background:
        rgba(88,101,242,0.1);

    border-color:
        rgba(88,101,242,0.25);
}

.discord-button {
    display: inline-flex;

    justify-content: center;

    align-items: center;

    margin-top: 18px;

    padding:
        10px 14px;

    border-radius: 9px;

    color: white;

    background:
        rgba(88,101,242,0.15);

    border:
        1px solid
        rgba(88,101,242,0.3);

    text-decoration: none;

    font-size: 12px;

    font-weight: 700;

    transition:
        0.2s ease;
}

.discord-button:hover {
    transform:
        translateY(-2px);

    background:
        rgba(88,101,242,0.25);

    border-color:
        rgba(88,101,242,0.5);

    box-shadow:
        0 8px 25px
        rgba(88,101,242,0.15);
}

/* ============================================================
   FOOTER
   ============================================================ */

footer {
    position: relative;

    z-index: 5;

    padding: 25px;

    text-align: center;

    color: #555560;

    font-size: 11px;
}

/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    header {
        padding: 20px;
    }

    .status {
        display: none;
    }

    h1 {
        letter-spacing: -4px;
    }

    .subtitle {
        font-size: 15px;
    }

    .buttons {
        flex-direction: column;
    }

    .button {
        width: 100%;

        max-width: 350px;
    }

    .features {
        grid-template-columns: 1fr;

        margin-top: 55px;
    }
}

</style>

</head>

<body>

<div class="background">

    <div class="grid"></div>

    <div class="glow glow-one"></div>

    <div class="glow glow-two"></div>

</div>

<header>

    <div class="logo">
        GEN<span>GA</span>
    </div>

    <div class="status">

        <span class="status-dot"></span>

        SYSTEM ONLINE

    </div>

</header>

<main>

<section class="hero">

<div class="badge">
    Genga Client • Next Generation
</div>

<h1>
    GENGA<br>
    CLIENT
</h1>

<p class="subtitle">
    The Next Generation of cheating.
</p>

{% if message %}

<div class="message">
    {{ message }}
</div>

{% endif %}

{% if download_ready %}

<div class="key-box">

    <h2>
        ✓ Key bestätigt
    </h2>

    <p>
        Dein Key wurde bestätigt.
        Du kannst den Client jetzt herunterladen.
    </p>

    <a
        class="button primary"
        href="/download/{{ request_id }}"
    >
        Download GENGA-client →
    </a>

</div>

{% else %}

<div class="buttons">

    <a
        class="button primary"
        href="#key"
    >
        Get GENGA-client&nbsp; →
    </a>

    <a
        class="button secondary"
        href="#features"
    >
        Learn more and Join The Discord
    </a>

</div>

<div
    class="key-box"
    id="key"
>

    <h2>
        🔐 Enter your key
    </h2>

    <p>
        Gib deinen Genga-Key ein, um einen Download anzufordern.
    </p>

    <form
        method="POST"
        action="/request-download"
    >

        <input
            class="key-input"
            type="password"
            name="key"
            placeholder="GENGA-XXXX-XXXX"
            required
            autocomplete="off"
        >

        <button
            class="key-submit"
            type="submit"
        >
            Key überprüfen
        </button>

    </form>

</div>

{% endif %}

<div
    class="features"
    id="features"
>

<div class="card">

    <div class="icon">
        ⚡
    </div>

    <h3>
        Fast Access
    </h3>

    <p>
        GENGA-Client Is a fast and easy to use minecraft cheat Client.
    </p>

</div>

<div class="card">

    <div class="icon">
        📢
    </div>

    <h3>
        Modern Interface
    </h3>

    <p>
        It has a clean, nice Interface
    </p>

</div>

<div class="card discord-card">

    <div class="icon discord-icon">
        💬
    </div>

    <h3>
        Discord
    </h3>

    <p>
        Tritt dem offiziellen
        Genga Client Discord bei.
    </p>

    <a
        class="discord-button"
        href="{{ discord_url }}"
        target="_blank"
        rel="noopener noreferrer"
    >
        Discord beitreten →
    </a>

</div>

</div>

</section>

</main>

<footer>
    © 2026 Genga Client
</footer>

</body>

</html>
"""


# ============================================================
# HAUPTSEITE
# ============================================================

@app.route("/")
def index():

    request_id = request.args.get("request")

    download_ready = False
    message = None

    if request_id:

        data = PENDING_REQUESTS.get(request_id)

        if data:

            if data["approved"]:
                download_ready = True

            else:
                message = (
                    "⏳ Dein Key wurde an das Genga-Team "
                    "gesendet. Warte auf die Bestätigung."
                )

    return render_template_string(
        HTML,
        discord_url=DISCORD_URL,
        download_ready=download_ready,
        request_id=request_id,
        message=message
    )


# ============================================================
# KEY ANFORDERN
# ============================================================

@app.route(
    "/request-download",
    methods=["POST"]
)
def request_download():

    entered_key = request.form.get(
        "key",
        ""
    ).strip()

    # --------------------------------------------------------
    # Leerer Key
    # --------------------------------------------------------

    if not entered_key:

        return render_template_string(
            HTML,
            discord_url=DISCORD_URL,
            download_ready=False,
            request_id=None,
            message="❌ Bitte gib einen Key ein."
        )

    # --------------------------------------------------------
    # Key überprüfen
    # --------------------------------------------------------

    if entered_key not in VALID_KEYS:

        return render_template_string(
            HTML,
            discord_url=DISCORD_URL,
            download_ready=False,
            request_id=None,
            message="❌ Dieser Key ist ungültig."
        )

    # --------------------------------------------------------
    # Request erstellen
    # --------------------------------------------------------

    request_id = uuid.uuid4().hex

    PENDING_REQUESTS[request_id] = {
        "key": entered_key,
        "approved": False,
        "created": time.time()
    }

    # --------------------------------------------------------
    # Discord Webhook
    # --------------------------------------------------------

    if DISCORD_WEBHOOK_URL:

        try:

            payload = {
                "content": "🔐 **Neue Genga Key-Anfrage**",

                "embeds": [
                    {
                        "title": "Genga Download Request",

                        "description":
                            "Ein Benutzer möchte den Client herunterladen.",

                        "fields": [

                            {
                                "name": "Key",
                                "value":
                                    f"`{entered_key}`",
                                "inline": False
                            },

                            {
                                "name": "Request ID",
                                "value":
                                    f"`{request_id}`",
                                "inline": False
                            }

                        ]
                    }
                ]
            }

            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=5
            )

            print(
                "Discord Webhook Status:",
                response.status_code
            )

        except Exception as error:

            print(
                "Discord Webhook Fehler:",
                error
            )

    else:

        print(
            "WARNUNG: DISCORD_WEBHOOK_URL ist nicht gesetzt."
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
    "/status/<request_id>"
)
def status(request_id):

    data = PENDING_REQUESTS.get(
        request_id
    )

    if not data:

        return jsonify({
            "status": "not_found"
        }), 404

    if data["approved"]:

        return jsonify({
            "status": "approved"
        })

    return jsonify({
        "status": "pending"
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin_login():

    # Bereits eingeloggt
    if session.get(
        "admin_authenticated"
    ):

        return redirect(
            url_for("admin_panel")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        # Passwort niemals aus dem HTML nehmen.
        # Es kommt ausschließlich aus Environment.
        if (
            ADMIN_PASSWORD
            and password == ADMIN_PASSWORD
        ):

            session.clear()

            session[
                "admin_authenticated"
            ] = True

            return redirect(
                url_for("admin_panel")
            )

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>

            <head>

                <meta charset="UTF-8">

                <title>Genga Admin</title>

                <style>

                    * {
                        box-sizing:border-box;
                    }

                    body {
                        margin:0;
                        min-height:100vh;

                        display:flex;
                        align-items:center;
                        justify-content:center;

                        background:#050507;

                        color:white;

                        font-family:
                            Arial,
                            sans-serif;
                    }

                    .box {
                        width:350px;

                        padding:30px;

                        border-radius:16px;

                        background:#111118;

                        border:
                            1px solid
                            rgba(255,255,255,.1);
                    }

                    h1 {
                        margin-top:0;
                    }

                    input {
                        width:100%;

                        padding:13px;

                        margin:
                            15px 0;

                        border-radius:8px;

                        border:
                            1px solid #333;

                        background:#050507;

                        color:white;

                        outline:none;
                    }

                    button {
                        width:100%;

                        padding:13px;

                        border:0;

                        border-radius:8px;

                        background:
                            linear-gradient(
                                135deg,
                                #7c3aed,
                                #4f46e5
                            );

                        color:white;

                        font-weight:bold;

                        cursor:pointer;
                    }

                    .error {
                        color:#f87171;

                        font-size:13px;
                    }

                </style>

            </head>

            <body>

                <div class="box">

                    <h1>
                        Genga Admin
                    </h1>

                    <p>
                        Admin Login
                    </p>

                    <p class="error">
                        Falsches Passwort.
                    </p>

                    <form method="POST">

                        <input
                            type="password"
                            name="password"
                            placeholder="Admin Passwort"
                            autocomplete="current-password"
                            required
                        >

                        <button>
                            Login
                        </button>

                    </form>

                </div>

            </body>

            </html>
            """
        )

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>Genga Admin</title>

        <style>

            * {
                box-sizing:border-box;
            }

            body {
                margin:0;
                min-height:100vh;

                display:flex;
                align-items:center;
                justify-content:center;

                background:#050507;

                color:white;

                font-family:
                    Arial,
                    sans-serif;
            }

            .box {
                width:350px;

                padding:30px;

                border-radius:16px;

                background:#111118;

                border:
                    1px solid
                    rgba(255,255,255,.1);
            }

            input {
                width:100%;

                padding:13px;

                margin:15px 0;

                border-radius:8px;

                border:
                    1px solid #333;

                background:#050507;

                color:white;

                outline:none;
            }

            button {
                width:100%;

                padding:13px;

                border:0;

                border-radius:8px;

                background:
                    linear-gradient(
                        135deg,
                        #7c3aed,
                        #4f46e5
                    );

                color:white;

                font-weight:bold;

                cursor:pointer;
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h1>
                Genga Admin
            </h1>

            <p>
                Admin Login
            </p>

            <form method="POST">

                <input
                    type="password"
                    name="password"
                    placeholder="Admin Passwort"
                    autocomplete="current-password"
                    required
                >

                <button>
                    Login
                </button>

            </form>

        </div>

    </body>

    </html>
    """


# ============================================================
# ADMIN PANEL
# ============================================================

@app.route(
    "/admin/panel"
)
@admin_required
def admin_panel():

    requests_html = ""

    if not PENDING_REQUESTS:

        requests_html = """
        <div class="empty">
            Keine Download-Anfragen vorhanden.
        </div>
        """

    else:

        # Neueste Anfragen zuerst
        sorted_requests = sorted(
            PENDING_REQUESTS.items(),
            key=lambda item: item[1]["created"],
            reverse=True
        )

        for request_id, data in sorted_requests:

            age = int(
                time.time()
                - data["created"]
            )

            if data["approved"]:

                status_html = """
                <div class="approved">
                    ✓ APPROVED
                </div>
                """

                button_html = ""

            else:

                status_html = """
                <div class="pending">
                    ⏳ PENDING
                </div>
                """

                button_html = f"""
                <form
                    method="POST"
                    action="/admin/approve/{request_id}"
                >

                    <button class="approve">
                        ✓ Key bestätigen
                    </button>

                </form>
                """

            requests_html += f"""

            <div class="request">

                {status_html}

                <p>
                    <strong>Request ID</strong>
                </p>

                <code>
                    {request_id}
                </code>

                <p>
                    <strong>Key</strong>
                </p>

                <code>
                    {data["key"]}
                </code>

                <p>
                    <strong>Alter</strong>
                </p>

                <span>
                    {age} Sekunden
                </span>

                {button_html}

            </div>

            """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Genga Admin Panel</title>

        <style>

            * {{
                box-sizing:border-box;
            }}

            body {{
                margin:0;

                min-height:100vh;

                padding:40px 20px;

                background:#050507;

                color:white;

                font-family:
                    Arial,
                    sans-serif;
            }}

            .container {{
                max-width:800px;

                margin:auto;
            }}

            h1 {{
                margin-bottom:8px;
            }}

            .subtitle {{
                color:#777;

                margin-bottom:30px;
            }}

            .request {{
                padding:25px;

                margin-bottom:15px;

                background:#111118;

                border:
                    1px solid
                    rgba(255,255,255,.1);

                border-radius:15px;
            }}

            .request p {{
                margin-top:18px;
                margin-bottom:6px;
            }}

            code {{
                display:block;

                padding:10px;

                border-radius:7px;

                background:#050507;

                color:#c4b5fd;

                word-break:break-all;
            }}

            .pending {{
                color:#facc15;

                font-weight:bold;
            }}

            .approved {{
                color:#4ade80;

                font-weight:bold;
            }}

            button {{
                margin-top:20px;

                padding:12px 18px;

                border:0;

                border-radius:8px;

                color:white;

                font-weight:bold;

                cursor:pointer;
            }}

            .approve {{
                background:#7c3aed;
            }}

            .approve:hover {{
                background:#6d28d9;
            }}

            .empty {{
                padding:25px;

                border-radius:15px;

                background:#111118;

                color:#777;
            }}

            .logout {{
                display:inline-block;

                margin-bottom:30px;

                color:#aaa;

                text-decoration:none;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>
                Genga Admin Panel
            </h1>

            <p class="subtitle">
                Download-Anfragen verwalten
            </p>

            <a
                class="logout"
                href="/admin/logout"
            >
                Abmelden
            </a>

            {requests_html}

        </div>

    </body>

    </html>
    """


# ============================================================
# ADMIN KEY BESTÄTIGEN
# ============================================================

@app.route(
    "/admin/approve/<request_id>",
    methods=["POST"]
)
@admin_required
def approve(request_id):

    data = PENDING_REQUESTS.get(
        request_id
    )

    if not data:

        return (
            "Request nicht gefunden.",
            404
        )

    data["approved"] = True

    print(
        f"Request {request_id} wurde bestätigt."
    )

    return redirect(
        url_for("admin_panel")
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
        url_for("admin_login")
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route(
    "/download/<request_id>"
)
def download(request_id):

    data = PENDING_REQUESTS.get(
        request_id
    )

    # Request existiert nicht
    if not data:

        return (
            "Download nicht freigegeben.",
            403
        )

    # Noch nicht bestätigt
    if not data["approved"]:

        return (
            "Dein Key wurde noch nicht bestätigt.",
            403
        )

    # Datei suchen
    datei_pfad = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        DOWNLOAD_DATEI
    )

    # Datei existiert nicht
    if not os.path.isfile(
        datei_pfad
    ):

        return (
            "Download-Datei nicht gefunden.",
            404
        )

    # Download
    return send_file(
        datei_pfad,
        as_attachment=True,
        download_name=DOWNLOAD_DATEI
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),

        debug=False
    )
