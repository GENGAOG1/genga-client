from flask import (
    Flask,
    send_file,
    render_template_string,
    request,
    redirect,
    url_for,
    session
)
import os
import uuid
import requests
import time

app = Flask(__name__)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

# In Render setzen:
# GENGA_SECRET_KEY = irgendein langer zufälliger Wert
# GENGA_VALID_KEYS = KEY1,KEY2,KEY3
# DISCORD_WEBHOOK_URL = dein Discord Webhook
# ADMIN_PASSWORD = dein Admin Passwort

app.secret_key = os.environ.get(
    "GENGA_SECRET_KEY",
    "change-this-secret"
)

DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    ""
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    ""
)

# Mehrere Keys möglich:
# GENGA_VALID_KEYS="GENGA-123,GENGA-456,GENGA-789"
VALID_KEYS = [
    key.strip()
    for key in os.environ.get("GENGA_VALID_KEYS", "").split(",")
    if key.strip()
]

# ============================================================
# KONFIGURATION
# ============================================================

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

DISCORD_URL = "https://discord.gg/VEEV2gaeB"

# Pending Requests
# request_id -> Daten
PENDING_REQUESTS = {}

# ============================================================
# HTML
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Genga Client</title>

<style>

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

header {
    position: relative;
    z-index: 10;

    max-width: 1200px;
    margin: auto;

    padding: 28px 30px;

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

    padding: 9px 15px;

    border:
        1px solid
        rgba(255,255,255,0.1);

    border-radius: 999px;

    background:
        rgba(255,255,255,0.04);

    backdrop-filter: blur(15px);

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

    animation: pulse 2s infinite;
}

@keyframes pulse {

    0%, 100% {
        opacity: 1;
    }

    50% {
        opacity: 0.4;
    }
}

main {
    position: relative;
    z-index: 5;

    min-height:
        calc(100vh - 90px);

    display: flex;

    justify-content: center;
    align-items: center;

    padding: 70px 20px 100px;
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
    padding: 9px 16px;

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

.buttons {
    display: flex;

    justify-content: center;
    align-items: center;

    gap: 14px;

    margin-top: 40px;

    flex-wrap: wrap;
}

.button {
    min-width: 200px;

    padding: 16px 25px;

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
    transform: translateY(-4px);

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

    backdrop-filter: blur(15px);
}

.secondary:hover {
    transform: translateY(-4px);

    border-color:
        rgba(255,255,255,0.25);

    background:
        rgba(255,255,255,0.07);
}

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

    backdrop-filter: blur(18px);

    transition:
        transform 0.25s ease,
        border-color 0.25s ease;
}

.card:hover {
    transform: translateY(-6px);

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

    padding: 10px 14px;

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
}

.discord-button:hover {
    transform: translateY(-2px);

    background:
        rgba(88,101,242,0.25);

    border-color:
        rgba(88,101,242,0.5);
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

    backdrop-filter: blur(18px);
}

.key-box h2 {
    font-size: 18px;
    margin-bottom: 8px;
}

.key-box p {
    color: #858592;
    font-size: 13px;
    margin-bottom: 18px;
}

.key-input {
    width: 100%;

    padding: 14px 16px;

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
    border-color: #8b5cf6;
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
    margin-top: 18px;

    padding: 12px;

    border-radius: 10px;

    background:
        rgba(255,255,255,0.05);

    color: #aaa;

    font-size: 13px;
}

footer {
    position: relative;

    z-index: 5;

    padding: 25px;

    text-align: center;

    color: #555560;

    font-size: 11px;
}

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

    <h2>✓ Key bestätigt</h2>

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

<div class="card">

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
                    "⏳ Dein Key wurde gesendet. "
                    "Warte auf die Bestätigung."
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

@app.route("/request-download", methods=["POST"])
def request_download():

    entered_key = request.form.get("key", "").strip()

    # Key überprüfen
    if not entered_key:
        return redirect(url_for("index"))

    if entered_key not in VALID_KEYS:

        return render_template_string(
            HTML,
            discord_url=DISCORD_URL,
            download_ready=False,
            request_id=None,
            message="❌ Dieser Key ist ungültig."
        )

    # Neue Request-ID
    request_id = uuid.uuid4().hex[:12]

    PENDING_REQUESTS[request_id] = {
        "key": entered_key,
        "approved": False,
        "created": time.time()
    }

    # ========================================================
    # DISCORD WEBHOOK
    # ========================================================

    if DISCORD_WEBHOOK_URL:

        try:

            payload = {
                "embeds": [
                    {
                        "title": "🔐 Neuer Genga Download Request",
                        "description":
                            "Ein neuer Benutzer möchte den Genga Client herunterladen.",
                        "fields": [
                            {
                                "name": "Key",
                                "value": f"`{entered_key}`",
                                "inline": False
                            },
                            {
                                "name": "Request ID",
                                "value": f"`{request_id}`",
                                "inline": False
                            }
                        ]
                    }
                ]
            }

            requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=5
            )

        except Exception as error:

            print(
                "Discord Webhook Fehler:",
                error
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

@app.route("/status/<request_id>")
def status(request_id):

    data = PENDING_REQUESTS.get(request_id)

    if not data:
        return "Request nicht gefunden.", 404

    if data["approved"]:
        return "approved"

    return "pending"


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(
                url_for("admin")
            )

        return """
        <h2>Falsches Passwort</h2>
        <a href="/admin">Zurück</a>
        """

    if not session.get("admin"):

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Genga Admin</title>
            <style>
                body {
                    background:#050507;
                    color:white;
                    font-family:Arial;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    min-height:100vh;
                }

                form {
                    background:#111118;
                    padding:30px;
                    border-radius:15px;
                    width:350px;
                }

                input {
                    width:100%;
                    padding:13px;
                    margin:10px 0;
                    background:#050507;
                    color:white;
                    border:1px solid #333;
                    border-radius:8px;
                }

                button {
                    width:100%;
                    padding:13px;
                    background:#7c3aed;
                    color:white;
                    border:0;
                    border-radius:8px;
                    font-weight:bold;
                }
            </style>
        </head>

        <body>

            <form method="POST">

                <h2>Genga Admin</h2>

                <input
                    type="password"
                    name="password"
                    placeholder="Admin Passwort"
                    required
                >

                <button>
                    Login
                </button>

            </form>

        </body>
        </html>
        """

    # ========================================================
    # ADMIN PANEL
    # ========================================================

    requests_html = ""

    for request_id, data in PENDING_REQUESTS.items():

        age = int(time.time() - data["created"])

        status_text = (
            "✅ APPROVED"
            if data["approved"]
            else "⏳ PENDING"
        )

        requests_html += f"""

        <div class="request">

            <h3>
                {status_text}
            </h3>

            <p>
                Request ID:
                <code>{request_id}</code>
            </p>

            <p>
                Key:
                <code>{data["key"]}</code>
            </p>

            <p>
                Alter:
                {age} Sekunden
            </p>

            <form
                method="POST"
                action="/admin/approve/{request_id}"
            >

                <button>
                    ✓ Key bestätigen
                </button>

            </form>

        </div>

        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>Genga Admin</title>

        <style>

            body {{
                background:#050507;
                color:white;
                font-family:Arial;
                padding:40px;
            }}

            h1 {{
                margin-bottom:30px;
            }}

            .request {{
                max-width:600px;
                padding:25px;
                margin-bottom:15px;

                background:#111118;

                border:
                    1px solid
                    rgba(255,255,255,.1);

                border-radius:15px;
            }}

            code {{
                color:#c4b5fd;
            }}

            button {{
                margin-top:15px;
                padding:12px 18px;

                background:#7c3aed;
                color:white;

                border:0;
                border-radius:8px;

                cursor:pointer;

                font-weight:bold;
            }}

        </style>

    </head>

    <body>

        <h1>
            Genga Admin Panel
        </h1>

        {requests_html}

    </body>

    </html>
    """


# ============================================================
# ADMIN: KEY BESTÄTIGEN
# ============================================================

@app.route(
    "/admin/approve/<request_id>",
    methods=["POST"]
)
def approve(request_id):

    if not session.get("admin"):

        return "Nicht autorisiert.", 403

    data = PENDING_REQUESTS.get(request_id)

    if not data:

        return "Request nicht gefunden.", 404

    data["approved"] = True

    return redirect(
        url_for("admin")
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route("/download/<request_id>")
def download(request_id):

    data = PENDING_REQUESTS.get(request_id)

    if not data:

        return "Download nicht freigegeben.", 403

    if not data["approved"]:

        return "Dein Key wurde noch nicht bestätigt.", 403

    datei_pfad = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        DOWNLOAD_DATEI
    )

    if not os.path.isfile(datei_pfad):

        return "Download-Datei nicht gefunden.", 404

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
