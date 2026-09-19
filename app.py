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

app.secret_key = os.environ.get(
    "GENGA_SECRET_KEY",
    ""
)

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

ADMIN_URL = "https://genga-client.onrender.com/admin"


# ============================================================
# REQUEST STORAGE
# ============================================================

PENDING_REQUESTS = {}


# ============================================================
# ADMIN LOGIN CHECK
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get(
            "admin_authenticated"
        ):

            return redirect(
                url_for("admin_login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# MAIN HTML
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

<title>GENGA Client</title>


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

    background:
        #08080b;

    color: #eeeeef;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    -webkit-font-smoothing: antialiased;

    overflow-x: hidden;
}


/* ============================================================
   BACKGROUND GRID
   ============================================================ */

body::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background:

        linear-gradient(
            rgba(255,255,255,0.018) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(255,255,255,0.018) 1px,
            transparent 1px
        );

    background-size:
        42px 42px;

    mask-image:
        linear-gradient(
            to bottom,
            black,
            transparent 80%
        );

    opacity: 0.5;
}


/* ============================================================
   TOP PURPLE GLOW
   ============================================================ */

body::after {

    content: "";

    position: fixed;

    width: 500px;
    height: 500px;

    top: -280px;
    left: 50%;

    transform:
        translateX(-50%);

    background:
        rgba(124,58,237,0.09);

    filter:
        blur(120px);

    pointer-events: none;
}


/* ============================================================
   HEADER
   ============================================================ */

header {

    width: 100%;

    height: 70px;

    border-bottom:
        1px solid
        rgba(255,255,255,0.07);

    background:
        rgba(8,8,11,0.82);

    backdrop-filter:
        blur(18px);

    position: relative;

    z-index: 10;
}


.header-inner {

    max-width: 1120px;

    height: 100%;

    margin: auto;

    padding:
        0 24px;

    display: flex;

    align-items: center;

    justify-content: space-between;
}


/* ============================================================
   LOGO
   ============================================================ */

.logo {

    display: flex;

    align-items: center;

    gap: 11px;

    color: #ffffff;

    font-size: 15px;

    font-weight: 800;

    letter-spacing: 3px;
}


.logo-mark {

    width: 28px;
    height: 28px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 7px;

    background:
        #8b5cf6;

    color: #ffffff;

    font-size: 12px;

    font-weight: 900;

    box-shadow:
        0 0 0 1px
        rgba(255,255,255,0.08);
}


.logo span {

    color:
        #a78bfa;
}


/* ============================================================
   HEADER STATUS
   ============================================================ */

.status {

    display: flex;

    align-items: center;

    gap: 8px;

    color: #77777f;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.5px;
}


.status-dot {

    width: 6px;
    height: 6px;

    border-radius: 50%;

    background:
        #4ade80;

    box-shadow:
        0 0 8px
        rgba(74,222,128,0.65);
}


/* ============================================================
   MAIN
   ============================================================ */

main {

    position: relative;

    z-index: 2;

    width: 100%;
}


.hero {

    max-width: 1120px;

    margin: auto;

    padding:
        110px 24px 90px;
}


/* ============================================================
   HERO CONTENT
   ============================================================ */

.hero-content {

    max-width: 760px;

    margin: auto;

    text-align: center;
}


/* ============================================================
   VERSION BADGE
   ============================================================ */

.version {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding:
        6px 10px;

    margin-bottom:
        24px;

    border:
        1px solid
        rgba(139,92,246,0.22);

    border-radius: 6px;

    background:
        rgba(139,92,246,0.06);

    color:
        #a78bfa;

    font-size: 10px;

    font-weight: 700;

    letter-spacing: 1.3px;

    text-transform:
        uppercase;
}


.version-dot {

    width: 5px;
    height: 5px;

    border-radius: 50%;

    background:
        #8b5cf6;
}


/* ============================================================
   TITLE
   ============================================================ */

h1 {

    font-size:
        clamp(52px, 9vw, 92px);

    line-height:
        0.95;

    font-weight:
        900;

    letter-spacing:
        -5px;

    color:
        #f5f5f5;

    margin-bottom:
        24px;
}


h1 span {

    color:
        #8b5cf6;
}


/* ============================================================
   SUBTITLE
   ============================================================ */

.subtitle {

    max-width:
        560px;

    margin:
        auto;

    color:
        #85858e;

    font-size:
        15px;

    line-height:
        1.7;
}


/* ============================================================
   ACTION BUTTONS
   ============================================================ */

.actions {

    display:
        flex;

    justify-content:
        center;

    gap:
        10px;

    margin-top:
        34px;

    flex-wrap:
        wrap;
}


.button {

    height:
        43px;

    padding:
        0 18px;

    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        8px;

    text-decoration:
        none;

    font-size:
        12px;

    font-weight:
        750;

    transition:
        0.18s ease;
}


.primary {

    background:
        #8b5cf6;

    color:
        white;

    box-shadow:
        0 5px 20px
        rgba(139,92,246,0.16);
}


.primary:hover {

    background:
        #7c3aed;

    transform:
        translateY(-1px);
}


.secondary {

    color:
        #b5b5bd;

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid
        rgba(255,255,255,0.09);
}


.secondary:hover {

    color:
        white;

    border-color:
        rgba(255,255,255,0.16);

    background:
        rgba(255,255,255,0.055);
}


/* ============================================================
   KEY PANEL
   ============================================================ */

.key-panel {

    width:
        100%;

    max-width:
        470px;

    margin:
        48px auto 0;

    padding:
        22px;

    border:
        1px solid
        rgba(255,255,255,0.08);

    border-radius:
        12px;

    background:
        #0e0e13;

    box-shadow:
        0 18px 60px
        rgba(0,0,0,0.22);
}


.panel-header {

    display:
        flex;

    align-items:
        center;

    gap:
        10px;

    margin-bottom:
        7px;
}


.panel-icon {

    width:
        27px;

    height:
        27px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        6px;

    background:
        rgba(139,92,246,0.1);

    border:
        1px solid
        rgba(139,92,246,0.18);

    color:
        #a78bfa;

    font-size:
        12px;
}


.key-panel h2 {

    font-size:
        13px;

    font-weight:
        750;

    color:
        #eeeeef;
}


.key-panel-description {

    margin-bottom:
        18px;

    color:
        #707079;

    font-size:
        11px;

    line-height:
        1.6;
}


/* ============================================================
   KEY INPUT
   ============================================================ */

.key-input {

    width:
        100%;

    height:
        43px;

    padding:
        0 13px;

    border:
        1px solid
        rgba(255,255,255,0.09);

    border-radius:
        7px;

    outline:
        none;

    background:
        #08080b;

    color:
        white;

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    font-size:
        12px;

    transition:
        border-color 0.18s ease;
}


.key-input::placeholder {

    color:
        #4f4f57;
}


.key-input:focus {

    border-color:
        rgba(139,92,246,0.6);
}


/* ============================================================
   KEY BUTTON
   ============================================================ */

.key-submit {

    width:
        100%;

    height:
        41px;

    margin-top:
        9px;

    border:
        none;

    border-radius:
        7px;

    background:
        #8b5cf6;

    color:
        white;

    font-size:
        11px;

    font-weight:
        800;

    cursor:
        pointer;

    transition:
        0.18s ease;
}


.key-submit:hover {

    background:
        #7c3aed;
}


/* ============================================================
   MESSAGE
   ============================================================ */

.message {

    max-width:
        470px;

    margin:
        22px auto 0;

    padding:
        13px 15px;

    border:
        1px solid
        rgba(255,255,255,0.07);

    border-radius:
        8px;

    background:
        #0e0e13;

    color:
        #8e8e97;

    font-size:
        11px;

    text-align:
        left;
}


/* ============================================================
   DOWNLOAD PANEL
   ============================================================ */

.download-panel {

    width:
        100%;

    max-width:
        470px;

    margin:
        48px auto 0;

    padding:
        22px;

    border:
        1px solid
        rgba(74,222,128,0.14);

    border-radius:
        12px;

    background:
        #0d100f;

    text-align:
        left;
}


.download-title {

    display:
        flex;

    align-items:
        center;

    gap:
        9px;

    margin-bottom:
        8px;

    color:
        #86efac;

    font-size:
        13px;

    font-weight:
        800;
}


.download-check {

    width:
        25px;

    height:
        25px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        6px;

    background:
        rgba(74,222,128,0.1);

    font-size:
        12px;
}


.download-description {

    margin-bottom:
        17px;

    color:
        #727a75;

    font-size:
        11px;

    line-height:
        1.6;
}


.download-button {

    width:
        100%;

    height:
        42px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        7px;

    background:
        #4ade80;

    color:
        #06130a;

    text-decoration:
        none;

    font-size:
        11px;

    font-weight:
        850;

    transition:
        0.18s ease;
}


.download-button:hover {

    background:
        #22c55e;

    transform:
        translateY(-1px);
}


/* ============================================================
   FEATURES
   ============================================================ */

.features-wrapper {

    max-width:
        900px;

    margin:
        90px auto 0;
}


.section-label {

    margin-bottom:
        14px;

    color:
        #56565e;

    font-size:
        9px;

    font-weight:
        800;

    letter-spacing:
        2px;

    text-transform:
        uppercase;
}


.features {

    display:
        grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:
        10px;
}


.card {

    min-height:
        160px;

    padding:
        20px;

    border:
        1px solid
        rgba(255,255,255,0.065);

    border-radius:
        10px;

    background:
        rgba(255,255,255,0.018);

    transition:
        0.2s ease;
}


.card:hover {

    background:
        rgba(255,255,255,0.028);

    border-color:
        rgba(255,255,255,0.11);

    transform:
        translateY(-2px);
}


.card-icon {

    width:
        31px;

    height:
        31px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    margin-bottom:
        15px;

    border-radius:
        7px;

    background:
        rgba(139,92,246,0.08);

    border:
        1px solid
        rgba(139,92,246,0.12);

    color:
        #a78bfa;

    font-size:
        13px;
}


.card h3 {

    margin-bottom:
        7px;

    color:
        #dddddf;

    font-size:
        12px;

    font-weight:
        750;
}


.card p {

    color:
        #696970;

    font-size:
        11px;

    line-height:
        1.65;
}


/* ============================================================
   DISCORD
   ============================================================ */

.discord-icon {

    color:
        #7289da;

    background:
        rgba(114,137,218,0.08);

    border-color:
        rgba(114,137,218,0.14);
}


.discord-button {

    display:
        inline-flex;

    align-items:
        center;

    margin-top:
        15px;

    padding:
        7px 10px;

    border-radius:
        6px;

    background:
        rgba(114,137,218,0.09);

    border:
        1px solid
        rgba(114,137,218,0.16);

    color:
        #9baeea;

    text-decoration:
        none;

    font-size:
        10px;

    font-weight:
        750;

    transition:
        0.18s ease;
}


.discord-button:hover {

    background:
        rgba(114,137,218,0.16);

    color:
        white;
}


/* ============================================================
   FOOTER
   ============================================================ */

footer {

    position:
        relative;

    z-index:
        2;

    max-width:
        1120px;

    margin:
        auto;

    padding:
        25px 24px 35px;

    border-top:
        1px solid
        rgba(255,255,255,0.055);

    color:
        #45454d;

    font-size:
        10px;

    text-align:
        center;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    .hero {

        padding:
            75px 18px 65px;
    }


    h1 {

        font-size:
            54px;

        letter-spacing:
            -4px;
    }


    .subtitle {

        font-size:
            13px;
    }


    .actions {

        flex-direction:
            column;

        align-items:
            center;
    }


    .button {

        width:
            100%;

        max-width:
            320px;
    }


    .features {

        grid-template-columns:
            1fr;
    }


    .features-wrapper {

        margin-top:
            65px;
    }


    .status {

        display:
            none;
    }

}

</style>

</head>


<body>


<!-- ==========================================================
     HEADER
     ========================================================== -->

<header>

    <div class="header-inner">

        <div class="logo">

            <div class="logo-mark">
                G
            </div>

            GEN<span>GA</span>

        </div>


        <div class="status">

            <span class="status-dot"></span>

            ONLINE

        </div>

    </div>

</header>


<!-- ==========================================================
     MAIN
     ========================================================== -->

<main>

<section class="hero">


    <!-- ======================================================
         HERO
         ====================================================== -->

    <div class="hero-content">


        <div class="version">

            <span class="version-dot"></span>

            GENGA CLIENT · 1.21.11

        </div>


        <h1>

            GENGA<span>.</span>

        </h1>


        <p class="subtitle">

            A clean and lightweight Minecraft client
            built for performance, control and simplicity.

        </p>


        <div class="actions">


            <a
                class="button primary"
                href="#key"
            >
                Get GENGA
            </a>


            <a
                class="button secondary"
                href="#features"
            >
                Explore Client
            </a>


        </div>


    </div>


    <!-- ======================================================
         MESSAGE
         ====================================================== -->

    {% if message %}

    <div class="message">

        {{ message }}

    </div>

    {% endif %}


    <!-- ======================================================
         DOWNLOAD READY
         ====================================================== -->

    {% if download_ready %}


    <div class="download-panel">


        <div class="download-title">

            <div class="download-check">
                ✓
            </div>

            Key verified

        </div>


        <p class="download-description">

            Your key has been approved.
            The GENGA Client download is now available.

        </p>


        <a
            class="download-button"
            href="/download/{{ request_id }}"
        >

            Download GENGA Client →

        </a>


    </div>


    {% else %}


    <!-- ======================================================
         KEY PANEL
         ====================================================== -->

    <div
        class="key-panel"
        id="key"
    >


        <div class="panel-header">


            <div class="panel-icon">
                #
            </div>


            <h2>
                Access Key
            </h2>


        </div>


        <p class="key-panel-description">

            Enter your GENGA access key to request
            access to the client download.

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

                Verify Key

            </button>


        </form>


    </div>


    {% endif %}


    <!-- ======================================================
         FEATURES
         ====================================================== -->

    <div
        class="features-wrapper"
        id="features"
    >


        <div class="section-label">
            Client
        </div>


        <div class="features">


            <!-- ==================================================
                 FEATURE 1
                 ================================================== -->

            <div class="card">


                <div class="card-icon">
                    ⚡
                </div>


                <h3>
                    Lightweight
                </h3>


                <p>

                    Designed to stay fast and responsive
                    without unnecessary interface elements.

                </p>


            </div>


            <!-- ==================================================
                 FEATURE 2
                 ================================================== -->

            <div class="card">


                <div class="card-icon">
                    ◈
                </div>


                <h3>
                    Modern Interface
                </h3>


                <p>

                    A minimal interface focused on
                    modules, settings and usability.

                </p>


            </div>


            <!-- ==================================================
                 FEATURE 3
                 ================================================== -->

            <div class="card discord-card">


                <div class="card-icon discord-icon">
                    💬
                </div>


                <h3>
                    Community
                </h3>


                <p>

                    Join the GENGA community for updates,
                    announcements and support.

                </p>


                <a
                    class="discord-button"
                    href="{{ discord_url }}"
                    target="_blank"
                    rel="noopener noreferrer"
                >

                    Join Discord →

                </a>


            </div>


        </div>


    </div>


</section>

</main>


<!-- ==========================================================
     FOOTER
     ========================================================== -->

<footer>

    © 2026 GENGA Client

</footer>


<!-- ==========================================================
     REQUEST STATUS
     ========================================================== -->

<script>

const requestId =
    "{{ request_id or '' }}";


if (requestId) {


    const checkStatus = async () => {


        try {


            const response =
                await fetch(
                    "/status/" +
                    encodeURIComponent(requestId),
                    {
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                return;

            }


            const data =
                await response.json();


            if (
                data.status === "approved"
            ) {


                window.location.reload();


            }


        } catch (error) {


            console.log(
                "Status check failed:",
                error
            );


        }


    };


    checkStatus();


    setInterval(
        checkStatus,
        2000
    );


}

</script>


</body>

</html>
"""


# ============================================================
# HAUPTSEITE
# ============================================================

@app.route("/")
def index():

    request_id = request.args.get(
        "request"
    )

    download_ready = False

    message = None


    if request_id:

        data = PENDING_REQUESTS.get(
            request_id
        )


        if data:

            if data["approved"]:

                download_ready = True

            else:

                message = (
                    "⏳ Dein Key wurde an das "
                    "Genga-Team gesendet. "
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
    # LEERER KEY
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
    # KEY ÜBERPRÜFEN
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
    # REQUEST ERSTELLEN
    # --------------------------------------------------------

    request_id = uuid.uuid4().hex


    PENDING_REQUESTS[request_id] = {

        "key": entered_key,

        "approved": False,

        "created": time.time()

    }


    # --------------------------------------------------------
    # DISCORD WEBHOOK
    # --------------------------------------------------------

    if DISCORD_WEBHOOK_URL:

        try:

            payload = {

                "content":
                    "🔐 **Neue Genga Key-Anfrage**",

                "embeds": [

                    {

                        "title":
                            "Genga Download Request",

                        "description":
                            "Ein Benutzer möchte "
                            "den Client herunterladen.",

                        "fields": [

                            {

                                "name":
                                    "Key",

                                "value":
                                    f"`{entered_key}`",

                                "inline":
                                    False

                            },

                            {

                                "name":
                                    "Request ID",

                                "value":
                                    f"`{request_id}`",

                                "inline":
                                    False

                            },

                            {

                                "name":
                                    "🛠️ Admin Panel",

                                "value":
                                    ADMIN_URL,

                                "inline":
                                    False

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
            "WARNUNG: "
            "DISCORD_WEBHOOK_URL ist nicht gesetzt."
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

            "status":
                "not_found"

        }), 404


    if data["approved"]:

        return jsonify({

            "status":
                "approved"

        })


    return jsonify({

        "status":
            "pending"

    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin_login():


    # --------------------------------------------------------
    # BEREITS EINGELOGGT
    # --------------------------------------------------------

    if session.get(
        "admin_authenticated"
    ):

        return redirect(
            url_for("admin_panel")
        )


    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":


        password = request.form.get(
            "password",
            ""
        )


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

                <meta
                    name="viewport"
                    content="width=device-width, initial-scale=1.0"
                >

                <title>GENGA Admin</title>


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

                        background:#08080b;

                        color:white;

                        font-family:
                            Arial,
                            sans-serif;
                    }


                    .box {

                        width:
                            350px;

                        padding:
                            30px;

                        border-radius:
                            12px;

                        background:
                            #0e0e13;

                        border:
                            1px solid
                            rgba(255,255,255,.08);

                        box-shadow:
                            0 20px 70px
                            rgba(0,0,0,.3);
                    }


                    .brand {

                        color:
                            #a78bfa;

                        font-size:
                            10px;

                        font-weight:
                            800;

                        letter-spacing:
                            2px;

                        margin-bottom:
                            10px;
                    }


                    h1 {

                        margin:
                            0 0 7px;

                        font-size:
                            22px;
                    }


                    .description {

                        color:
                            #6f6f78;

                        font-size:
                            12px;

                        line-height:
                            1.6;
                    }


                    .error {

                        margin-top:
                            16px;

                        padding:
                            10px;

                        border-radius:
                            7px;

                        background:
                            rgba(248,113,113,.06);

                        border:
                            1px solid
                            rgba(248,113,113,.12);

                        color:
                            #f87171;

                        font-size:
                            11px;
                    }


                    input {

                        width:
                            100%;

                        height:
                            42px;

                        padding:
                            0 12px;

                        margin:
                            18px 0 9px;

                        border-radius:
                            7px;

                        border:
                            1px solid
                            rgba(255,255,255,.09);

                        background:
                            #08080b;

                        color:
                            white;

                        outline:
                            none;
                    }


                    input:focus {

                        border-color:
                            rgba(139,92,246,.6);
                    }


                    button {

                        width:
                            100%;

                        height:
                            41px;

                        border:
                            0;

                        border-radius:
                            7px;

                        background:
                            #8b5cf6;

                        color:
                            white;

                        font-weight:
                            800;

                        cursor:
                            pointer;
                    }


                    button:hover {

                        background:
                            #7c3aed;
                    }

                </style>

            </head>


            <body>


                <div class="box">


                    <div class="brand">
                        GENGA ADMIN
                    </div>


                    <h1>
                        Admin Login
                    </h1>


                    <p class="description">
                        Sign in to manage
                        download requests.
                    </p>


                    <div class="error">
                        Falsches Passwort.
                    </div>


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


    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    return """

    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>GENGA Admin</title>


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

                background:#08080b;

                color:white;

                font-family:
                    Arial,
                    sans-serif;
            }


            .box {

                width:
                    350px;

                padding:
                    30px;

                border-radius:
                    12px;

                background:
                    #0e0e13;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                box-shadow:
                    0 20px 70px
                    rgba(0,0,0,.3);
            }


            .brand {

                color:
                    #a78bfa;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    2px;

                margin-bottom:
                    10px;
            }


            h1 {

                margin:
                    0 0 7px;

                font-size:
                    22px;
            }


            .description {

                color:
                    #6f6f78;

                font-size:
                    12px;

                line-height:
                    1.6;
            }


            input {

                width:
                    100%;

                height:
                    42px;

                padding:
                    0 12px;

                margin:
                    18px 0 9px;

                border-radius:
                    7px;

                border:
                    1px solid
                    rgba(255,255,255,.09);

                background:
                    #08080b;

                color:
                    white;

                outline:
                    none;
            }


            input:focus {

                border-color:
                    rgba(139,92,246,.6);
            }


            button {

                width:
                    100%;

                height:
                    41px;

                border:
                    0;

                border-radius:
                    7px;

                background:
                    #8b5cf6;

                color:
                    white;

                font-weight:
                    800;

                cursor:
                    pointer;
            }


            button:hover {

                background:
                    #7c3aed;
            }

        </style>

    </head>


    <body>


        <div class="box">


            <div class="brand">
                GENGA ADMIN
            </div>


            <h1>
                Admin Login
            </h1>


            <p class="description">
                Sign in to manage
                download requests.
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


    # --------------------------------------------------------
    # KEINE REQUESTS
    # --------------------------------------------------------

    if not PENDING_REQUESTS:


        requests_html = """

        <div class="empty">

            Keine Download-Anfragen vorhanden.

        </div>

        """


    # --------------------------------------------------------
    # REQUESTS
    # --------------------------------------------------------

    else:


        sorted_requests = sorted(

            PENDING_REQUESTS.items(),

            key=lambda item:
                item[1]["created"],

            reverse=True

        )


        for request_id, data in sorted_requests:


            age = int(

                time.time()
                -
                data["created"]

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
                    <strong>
                        Request ID
                    </strong>
                </p>


                <code>
                    {request_id}
                </code>


                <p>
                    <strong>
                        Key
                    </strong>
                </p>


                <code>
                    {data["key"]}
                </code>


                <p>
                    <strong>
                        Alter
                    </strong>
                </p>


                <span>
                    {age} Sekunden
                </span>


                {button_html}


            </div>

            """


    # --------------------------------------------------------
    # ADMIN HTML
    # --------------------------------------------------------

    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>
            GENGA Admin Panel
        </title>


        <style>

            * {{
                box-sizing:border-box;
            }}


            body {{

                margin:0;

                min-height:100vh;

                padding:
                    40px 20px;

                background:
                    #08080b;

                color:
                    white;

                font-family:
                    Arial,
                    sans-serif;
            }}


            .container {{

                max-width:
                    800px;

                margin:
                    auto;
            }}


            .brand {{

                color:
                    #a78bfa;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    2px;

                margin-bottom:
                    10px;
            }}


            h1 {{

                margin:
                    0 0 8px;
            }}


            .subtitle {{

                color:
                    #777;

                margin-bottom:
                    30px;

                font-size:
                    12px;
            }}


            .request {{

                padding:
                    22px;

                margin-bottom:
                    12px;

                background:
                    #0e0e13;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                border-radius:
                    11px;
            }}


            .request p {{

                margin-top:
                    18px;

                margin-bottom:
                    6px;

                color:
                    #aaa;

                font-size:
                    11px;
            }}


            code {{

                display:block;

                padding:
                    10px;

                border-radius:
                    7px;

                background:
                    #08080b;

                color:
                    #c4b5fd;

                word-break:
                    break-all;

                font-family:
                    Consolas,
                    monospace;

                font-size:
                    11px;
            }}


            .pending {{

                color:
                    #facc15;

                font-size:
                    11px;

                font-weight:
                    bold;
            }}


            .approved {{

                color:
                    #4ade80;

                font-size:
                    11px;

                font-weight:
                    bold;
            }}


            button {{

                margin-top:
                    18px;

                padding:
                    11px 16px;

                border:
                    0;

                border-radius:
                    7px;

                color:
                    white;

                font-weight:
                    bold;

                cursor:
                    pointer;
            }}


            .approve {{

                background:
                    #8b5cf6;
            }}


            .approve:hover {{

                background:
                    #7c3aed;
            }}


            .empty {{

                padding:
                    25px;

                border-radius:
                    11px;

                background:
                    #0e0e13;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                color:
                    #777;

                font-size:
                    12px;
            }}


            .logout {{

                display:
                    inline-block;

                margin-bottom:
                    30px;

                color:
                    #777;

                text-decoration:
                    none;

                font-size:
                    11px;
            }}


            .logout:hover {{

                color:
                    white;
            }}

        </style>

    </head>


    <body>


        <div class="container">


            <div class="brand">
                GENGA ADMIN
            </div>


            <h1>
                Admin Panel
            </h1>


            <p class="subtitle">
                Download-Anfragen verwalten
            </p>


            <a
                class="logout"
                href="/admin/logout"
            >

                Abmelden →

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
        f"Request {request_id} "
        f"wurde bestätigt."
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


    # --------------------------------------------------------
    # REQUEST EXISTIERT NICHT
    # --------------------------------------------------------

    if not data:

        return (
            "Download nicht freigegeben.",
            403
        )


    # --------------------------------------------------------
    # NICHT BESTÄTIGT
    # --------------------------------------------------------

    if not data["approved"]:

        return (
            "Dein Key wurde noch "
            "nicht bestätigt.",
            403
        )


    # --------------------------------------------------------
    # DATEIPFAD
    # --------------------------------------------------------

    datei_pfad = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        DOWNLOAD_DATEI

    )


    # --------------------------------------------------------
    # DATEI EXISTIERT NICHT
    # --------------------------------------------------------

    if not os.path.isfile(
        datei_pfad
    ):

        return (
            "Download-Datei nicht gefunden.",
            404
        )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

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
