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
import time
import requests
from functools import wraps


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

GENGA_SECRET_KEY = os.environ.get("GENGA_SECRET_KEY")

if not GENGA_SECRET_KEY:
    raise RuntimeError(
        "GENGA_SECRET_KEY fehlt in den Render Environment Variables."
    )

app.config["SECRET_KEY"] = GENGA_SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

VALID_KEYS = [
    key.strip()
    for key in os.environ.get("GENGA_VALID_KEYS", "").split(",")
    if key.strip()
]


# =========================================================
# SETTINGS
# =========================================================

DOWNLOAD_DATEI = "genga-client-1.21.11.txt"

DISCORD_URL = "https://discord.gg/VEEV2gaeB"

ADMIN_URL = "https://genga-client.onrender.com/admin"


# =========================================================
# REQUEST STORAGE
# =========================================================
#
# WICHTIG:
# Keys werden NICHT verbraucht.
#
# Ein Key kann während der Testphase beliebig oft
# neue Download-Anfragen erstellen.
#
# =========================================================

PENDING_REQUESTS = {}


# =========================================================
# ADMIN AUTH
# =========================================================

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login"))

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# MAIN PAGE
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Genga Client</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background:
        radial-gradient(circle at top, #1c1c1c 0%, #080808 45%, #030303 100%);
    color: white;
    font-family: Arial, Helvetica, sans-serif;
    min-height: 100vh;
}

.container {
    width: 90%;
    max-width: 1100px;
    margin: auto;
}

header {
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #222;
}

.logo {
    font-size: 25px;
    font-weight: 900;
    letter-spacing: 4px;
}

.status {
    color: #6cff8d;
    font-size: 13px;
}

.hero {
    min-height: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.badge {
    border: 1px solid #333;
    padding: 8px 15px;
    border-radius: 30px;
    color: #aaa;
    font-size: 13px;
    margin-bottom: 25px;
}

h1 {
    font-size: clamp(50px, 9vw, 100px);
    font-weight: 900;
    letter-spacing: -4px;
    line-height: 0.9;
}

.subtitle {
    color: #999;
    max-width: 650px;
    margin-top: 25px;
    line-height: 1.7;
}

.button {
    display: inline-block;
    margin-top: 35px;
    padding: 15px 30px;
    border-radius: 8px;
    background: white;
    color: black;
    text-decoration: none;
    font-weight: bold;
    transition: 0.2s;
}

.button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(255,255,255,0.15);
}

.key-section {
    max-width: 500px;
    width: 100%;
    margin-top: 40px;
}

.key-section h2 {
    margin-bottom: 15px;
}

.key-form {
    display: flex;
    gap: 10px;
}

.key-input {
    flex: 1;
    background: #111;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 15px;
    color: white;
    outline: none;
}

.key-input:focus {
    border-color: #777;
}

.key-button {
    border: none;
    background: white;
    color: black;
    padding: 0 20px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}

.message {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #333;
    border-radius: 8px;
    background: #101010;
    color: #ccc;
}

.download {
    margin-top: 20px;
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    padding: 60px 0;
}

.card {
    background: rgba(255,255,255,0.025);
    border: 1px solid #222;
    border-radius: 12px;
    padding: 25px;
}

.card h3 {
    margin-bottom: 10px;
}

.card p {
    color: #888;
    line-height: 1.5;
}

footer {
    border-top: 1px solid #222;
    padding: 30px 0;
    color: #666;
    text-align: center;
}

.discord {
    color: #aaa;
    text-decoration: none;
}

.discord:hover {
    color: white;
}

@media(max-width:600px) {

    .key-form {
        flex-direction: column;
    }

    .key-button {
        padding: 14px;
    }

}

</style>

</head>

<body>

<div class="container">

<header>

<div class="logo">
GENGA
</div>

<div class="status">
● SYSTEM ONLINE
</div>

</header>


<section class="hero">

<div class="badge">
GENGA CLIENT • TEST PHASE
</div>

<h1>
GENGA<br>
CLIENT
</h1>

<p class="subtitle">
Der Genga Client. Schnell, modern und für die aktuelle Testphase
bereitgestellt.
</p>


<a href="#key" class="button">
DOWNLOAD CLIENT
</a>


<div class="key-section" id="key">

<h2>
🔑 Key bestätigen
</h2>

<form action="/request-download" method="POST" class="key-form">

<input
    class="key-input"
    type="text"
    name="key"
    placeholder="GENGA-XXXX-XXXX"
    autocomplete="off"
    required
>

<button class="key-button" type="submit">
BESTÄTIGEN
</button>

</form>


{% if message %}

<div class="message">
{{ message }}
</div>

{% endif %}


{% if download_ready %}

<div class="download">

<a
    class="button"
    href="/download/{{ request_id }}"
>
⬇ CLIENT HERUNTERLADEN
</a>

</div>

{% endif %}

</div>

</section>


<section class="features">

<div class="card">

<h3>
⚡ Performance
</h3>

<p>
Optimiert für eine schnelle und flüssige Nutzung.
</p>

</div>


<div class="card">

<h3>
🔐 Key System
</h3>

<p>
Zugang über einen gültigen Genga Key.
</p>

</div>


<div class="card">

<h3>
🛠 Test Phase
</h3>

<p>
Der Client befindet sich aktuell in der Testphase.
</p>

</div>

</section>


<footer>

<a
    class="discord"
    href="{{ discord_url }}"
    target="_blank"
>
Discord Community
</a>

</footer>

</div>

</body>

</html>
"""


# =========================================================
# ADMIN LOGIN PAGE
# =========================================================

ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Genga Admin</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: #050505;
    color: white;
    font-family: Arial, Helvetica, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
}

.box {
    width: 90%;
    max-width: 400px;
    background: #101010;
    border: 1px solid #252525;
    border-radius: 14px;
    padding: 30px;
}

h1 {
    margin-top: 0;
    margin-bottom: 10px;
}

p {
    color: #777;
}

input {
    width: 100%;
    padding: 14px;
    margin-top: 15px;
    background: #080808;
    color: white;
    border: 1px solid #333;
    border-radius: 8px;
    outline: none;
}

button {
    width: 100%;
    margin-top: 15px;
    padding: 14px;
    background: white;
    color: black;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}

.error {
    margin-top: 15px;
    color: #ff6b6b;
}

</style>

</head>

<body>

<div class="box">

<h1>Genga Admin</h1>

<p>Admin Passwort eingeben.</p>

<form method="POST">

<input
    type="password"
    name="password"
    placeholder="Admin Passwort"
    required
>

<button type="submit">
LOGIN
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


# =========================================================
# HOME
# =========================================================

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
                    "⏳ Dein Key wurde an das Genga-Team gesendet. "
                    "Warte auf die Bestätigung."
                )

    return render_template_string(
        HTML,
        discord_url=DISCORD_URL,
        download_ready=download_ready,
        request_id=request_id,
        message=message
    )


# =========================================================
# REQUEST DOWNLOAD
# =========================================================

@app.route("/request-download", methods=["POST"])
def request_download():

    entered_key = request.form.get("key", "").strip()

    # Key prüfen
    if entered_key not in VALID_KEYS:

        return render_template_string(
            HTML,
            discord_url=DISCORD_URL,
            download_ready=False,
            request_id=None,
            message="❌ Ungültiger Key."
        ), 403


    # Neue Request-ID erstellen
    request_id = uuid.uuid4().hex


    # Request speichern
    #
    # Der Key wird NICHT entfernt.
    # Dadurch kann er unendlich oft verwendet werden.
    #
    PENDING_REQUESTS[request_id] = {
        "key": entered_key,
        "approved": False,
        "created": time.time()
    }


    # =====================================================
    # DISCORD WEBHOOK
    # =====================================================

    if DISCORD_WEBHOOK_URL:

        payload = {

            "content": "🔐 **Neue Genga Key-Anfrage**",

            "embeds": [

                {

                    "title": "Genga Download Request",

                    "description":
                        "Ein Benutzer möchte den Genga Client herunterladen.",

                    "fields": [

                        {
                            "name": "🔑 Key",
                            "value": f"`{entered_key}`",
                            "inline": False
                        },

                        {
                            "name": "🆔 Request ID",
                            "value": f"`{request_id}`",
                            "inline": False
                        },

                        {
                            "name": "🛠️ Admin Panel",
                            "value": ADMIN_URL,
                            "inline": False
                        }

                    ]

                }

            ]

        }

        try:

            requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                timeout=10
            )

        except requests.RequestException:

            pass


    return redirect(
        url_for(
            "index",
            request=request_id
        )
    )


# =========================================================
# REQUEST STATUS
# =========================================================

@app.route("/status/<request_id>")
def request_status(request_id):

    data = PENDING_REQUESTS.get(request_id)

    if not data:

        return jsonify({
            "status": "not_found"
        }), 404


    if data["approved"]:

        return jsonify({
            "status": "approved",
            "download": f"/download/{request_id}"
        })


    return jsonify({
        "status": "pending"
    })


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_authenticated"):

        return redirect(
            url_for("admin_panel")
        )


    error = None


    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if not ADMIN_PASSWORD:

            error = (
                "ADMIN_PASSWORD ist in den "
                "Render Environment Variables nicht gesetzt."
            )

        elif password == ADMIN_PASSWORD:

            session.clear()

            session["admin_authenticated"] = True

            session.modified = True

            return redirect(
                url_for("admin_panel")
            )

        else:

            error = "❌ Falsches Passwort."


    return render_template_string(
        ADMIN_LOGIN_HTML,
        error=error
    )


# =========================================================
# ADMIN PANEL
# =========================================================

@app.route("/admin/panel")
@admin_required
def admin_panel():

    requests_html = ""


    if not PENDING_REQUESTS:

        requests_html = """
        <div class="empty">
            Keine offenen Anfragen.
        </div>
        """


    for request_id, data in list(
        PENDING_REQUESTS.items()
    ):

        if data["approved"]:

            status = "✅ BESTÄTIGT"

            button = """
            <span class="approved">
                Bereits bestätigt
            </span>
            """

        else:

            status = "⏳ WARTEND"

            button = f"""
            <form
                method="POST"
                action="/admin/approve/{request_id}"
            >

                <button class="approve">
                    ✅ BESTÄTIGEN
                </button>

            </form>
            """


        requests_html += f"""

        <div class="request">

            <div>

                <div class="key">
                    🔑 {data["key"]}
                </div>

                <div class="id">
                    Request ID: {request_id}
                </div>

                <div class="status">
                    {status}
                </div>

            </div>

            <div>
                {button}
            </div>

        </div>

        """


    return f"""

<!DOCTYPE html>

<html lang="de">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Genga Admin Panel</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    min-height: 100vh;

    background: #050505;

    color: white;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

}}

.container {{

    width: 92%;

    max-width: 1000px;

    margin: auto;

    padding: 40px 0;

}}

.top {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 30px;

}}

h1 {{

    margin: 0;

}}

.logout {{

    color: #aaa;

    text-decoration: none;

}}

.logout:hover {{

    color: white;

}}

.request {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 20px;

    background: #101010;

    border: 1px solid #252525;

    border-radius: 12px;

    padding: 20px;

    margin-bottom: 12px;

}}

.key {{

    font-size: 18px;

    font-weight: bold;

}}

.id {{

    color: #666;

    font-size: 12px;

    margin-top: 7px;

    word-break: break-all;

}}

.status {{

    color: #aaa;

    margin-top: 8px;

}}

button {{

    border: none;

    border-radius: 8px;

    padding: 12px 18px;

    cursor: pointer;

    font-weight: bold;

}}

.approve {{

    background: white;

    color: black;

}}

.approved {{

    color: #6cff8d;

}}

.empty {{

    color: #777;

    padding: 30px;

    background: #101010;

    border-radius: 12px;

}}

@media(max-width:600px) {{

    .request {{

        flex-direction: column;

        align-items: flex-start;

    }}

}}

</style>

</head>

<body>

<div class="container">

<div class="top">

<h1>Genga Admin</h1>

<a
    class="logout"
    href="/admin/logout"
>
Logout
</a>

</div>

{requests_html}

</div>

</body>

</html>

"""


# =========================================================
# APPROVE REQUEST
# =========================================================

@app.route(
    "/admin/approve/<request_id>",
    methods=["POST"]
)
@admin_required
def approve_request(request_id):

    data = PENDING_REQUESTS.get(request_id)


    if not data:

        return "❌ Anfrage nicht gefunden", 404


    data["approved"] = True


    return redirect(
        url_for("admin_panel")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# DOWNLOAD
# =========================================================

@app.route("/download/<request_id>")
def download(request_id):

    data = PENDING_REQUESTS.get(request_id)


    if not data:

        return "❌ Anfrage nicht gefunden", 404


    if not data["approved"]:

        return "⏳ Anfrage wurde noch nicht bestätigt", 403


    if not os.path.exists(DOWNLOAD_DATEI):

        return (
            "❌ Download-Datei nicht gefunden",
            404
        )


    # =====================================================
    # WICHTIG:
    #
    # Hier wird der Key NICHT gelöscht.
    #
    # Derselbe Key kann deshalb beliebig oft verwendet
    # werden, solange er in GENGA_VALID_KEYS steht.
    #
    # =====================================================

    return send_file(

        DOWNLOAD_DATEI,

        as_attachment=True,

        download_name=DOWNLOAD_DATEI

    )


# =========================================================
# START
# =========================================================

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
