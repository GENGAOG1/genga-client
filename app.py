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


body {

    min-height: 100vh;

    background:
        #070707;

    color:
        #eeeeee;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    -webkit-font-smoothing:
        antialiased;

    overflow-x:
        hidden;
}


/* ============================================================
   SUBTLE BACKGROUND
   ============================================================ */

body::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background-image:

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
        45px 45px;

    mask-image:
        linear-gradient(
            to bottom,
            black,
            transparent 85%
        );

    opacity:
        0.35;
}


/* ============================================================
   SUBTLE RED / ORANGE LIGHT
   ============================================================ */

body::after {

    content: "";

    position: fixed;

    width:
        450px;

    height:
        450px;

    top:
        -300px;

    left:
        50%;

    transform:
        translateX(-50%);

    background:
        rgba(255,70,20,0.07);

    filter:
        blur(120px);

    pointer-events:
        none;
}


/* ============================================================
   HEADER
   ============================================================ */

header {

    width:
        100%;

    height:
        68px;

    border-bottom:
        1px solid
        rgba(255,255,255,0.07);

    background:
        rgba(7,7,7,0.92);

    backdrop-filter:
        blur(18px);

    position:
        relative;

    z-index:
        10;
}


.header-inner {

    max-width:
        1120px;

    height:
        100%;

    margin:
        auto;

    padding:
        0 24px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;
}


/* ============================================================
   LOGO
   ============================================================ */

.logo {

    display:
        flex;

    align-items:
        center;

    gap:
        11px;

    color:
        #ffffff;

    font-size:
        15px;

    font-weight:
        900;

    letter-spacing:
        3px;
}


.logo-mark {

    width:
        28px;

    height:
        28px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        6px;

    background:
        #ff3b16;

    color:
        #ffffff;

    font-size:
        11px;

    font-weight:
        950;

    box-shadow:
        0 0 18px
        rgba(255,59,22,0.18);
}


.logo span {

    color:
        #ff4d22;
}


/* ============================================================
   STATUS
   ============================================================ */

.status {

    display:
        flex;

    align-items:
        center;

    gap:
        8px;

    color:
        #686868;

    font-size:
        9px;

    font-weight:
        800;

    letter-spacing:
        1.5px;
}


.status-dot {

    width:
        6px;

    height:
        6px;

    border-radius:
        50%;

    background:
        #ff5a24;

    box-shadow:
        0 0 8px
        rgba(255,90,36,0.6);
}


/* ============================================================
   MAIN
   ============================================================ */

main {

    position:
        relative;

    z-index:
        2;

    width:
        100%;
}


.hero {

    max-width:
        1120px;

    margin:
        auto;

    padding:
        105px 24px 85px;
}


/* ============================================================
   HERO CONTENT
   ============================================================ */

.hero-content {

    max-width:
        760px;

    margin:
        auto;

    text-align:
        center;
}


/* ============================================================
   VERSION
   ============================================================ */

.version {

    display:
        inline-flex;

    align-items:
        center;

    gap:
        8px;

    padding:
        6px 10px;

    margin-bottom:
        24px;

    border:
        1px solid
        rgba(255,70,20,0.22);

    border-radius:
        5px;

    background:
        rgba(255,70,20,0.045);

    color:
        #ff7048;

    font-size:
        9px;

    font-weight:
        800;

    letter-spacing:
        1.4px;

    text-transform:
        uppercase;
}


.version-dot {

    width:
        5px;

    height:
        5px;

    border-radius:
        50%;

    background:
        #ff4d22;

    box-shadow:
        0 0 7px
        rgba(255,77,34,0.7);
}


/* ============================================================
   TITLE
   ============================================================ */

h1 {

    font-size:
        clamp(55px, 9vw, 95px);

    line-height:
        0.9;

    font-weight:
        950;

    letter-spacing:
        -5px;

    color:
        #f2f2f2;

    margin-bottom:
        23px;
}


h1 span {

    color:
        #ff4b21;
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
        #77777b;

    font-size:
        14px;

    line-height:
        1.7;
}


/* ============================================================
   ACTIONS
   ============================================================ */

.actions {

    display:
        flex;

    justify-content:
        center;

    gap:
        9px;

    margin-top:
        32px;

    flex-wrap:
        wrap;
}


.button {

    height:
        42px;

    padding:
        0 18px;

    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        7px;

    text-decoration:
        none;

    font-size:
        11px;

    font-weight:
        850;

    transition:
        0.18s ease;
}


/* ============================================================
   PRIMARY
   ============================================================ */

.primary {

    background:
        #ff461d;

    color:
        white;

    box-shadow:
        0 6px 22px
        rgba(255,70,29,0.14);
}


.primary:hover {

    background:
        #ff5728;

    transform:
        translateY(-1px);

    box-shadow:
        0 8px 28px
        rgba(255,70,29,0.22);
}


/* ============================================================
   SECONDARY
   ============================================================ */

.secondary {

    color:
        #a5a5a9;

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid
        rgba(255,255,255,0.08);
}


.secondary:hover {

    color:
        white;

    background:
        rgba(255,255,255,0.045);

    border-color:
        rgba(255,255,255,0.15);
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
        rgba(255,255,255,0.075);

    border-radius:
        10px;

    background:
        #0d0d0f;

    box-shadow:
        0 20px 60px
        rgba(0,0,0,0.25);
}


/* ============================================================
   PANEL HEADER
   ============================================================ */

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
        rgba(255,70,20,0.08);

    border:
        1px solid
        rgba(255,70,20,0.15);

    color:
        #ff633b;

    font-size:
        11px;

    font-weight:
        900;
}


.key-panel h2 {

    font-size:
        13px;

    font-weight:
        800;

    color:
        #e7e7e8;
}


.key-panel-description {

    margin-bottom:
        18px;

    color:
        #68686e;

    font-size:
        11px;

    line-height:
        1.6;
}


/* ============================================================
   INPUT
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
        rgba(255,255,255,0.08);

    border-radius:
        7px;

    outline:
        none;

    background:
        #070707;

    color:
        white;

    font-family:
        "SFMono-Regular",
        Consolas,
        monospace;

    font-size:
        11px;

    transition:
        border-color
        0.18s ease,
        box-shadow
        0.18s ease;
}


.key-input::placeholder {

    color:
        #454549;
}


.key-input:focus {

    border-color:
        rgba(255,70,20,0.55);

    box-shadow:
        0 0 0 2px
        rgba(255,70,20,0.06);
}


/* ============================================================
   KEY SUBMIT
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
        #ff461d;

    color:
        white;

    font-size:
        11px;

    font-weight:
        850;

    cursor:
        pointer;

    transition:
        0.18s ease;
}


.key-submit:hover {

    background:
        #ff5728;
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

    border-left:
        2px solid
        #ff4b21;

    border-radius:
        7px;

    background:
        #0d0d0f;

    color:
        #8a8a90;

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
        rgba(255,77,34,0.2);

    border-radius:
        10px;

    background:
        #0e0d0c;

    box-shadow:
        0 18px 60px
        rgba(0,0,0,0.25);
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
        #ff714c;

    font-size:
        13px;

    font-weight:
        850;
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
        rgba(255,70,20,0.1);

    border:
        1px solid
        rgba(255,70,20,0.15);

    color:
        #ff5b2c;

    font-size:
        12px;
}


.download-description {

    margin-bottom:
        17px;

    color:
        #74716f;

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
        #ff461d;

    color:
        white;

    text-decoration:
        none;

    font-size:
        11px;

    font-weight:
        850;

    transition:
        0.18s ease;

    box-shadow:
        0 6px 22px
        rgba(255,70,29,0.12);
}


.download-button:hover {

    background:
        #ff5728;

    transform:
        translateY(-1px);

    box-shadow:
        0 8px 28px
        rgba(255,70,29,0.2);
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
        13px;

    color:
        #4f4f53;

    font-size:
        9px;

    font-weight:
        850;

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
        rgba(255,255,255,0.06);

    border-radius:
        9px;

    background:
        rgba(255,255,255,0.016);

    transition:
        0.18s ease;
}


.card:hover {

    background:
        rgba(255,255,255,0.025);

    border-color:
        rgba(255,70,20,0.13);

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
        rgba(255,70,20,0.065);

    border:
        1px solid
        rgba(255,70,20,0.11);

    color:
        #ff653d;

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
        800;
}


.card p {

    color:
        #65656b;

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
        #ff7350;

    background:
        rgba(255,70,20,0.065);

    border-color:
        rgba(255,70,20,0.11);
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
        rgba(255,70,20,0.065);

    border:
        1px solid
        rgba(255,70,20,0.13);

    color:
        #ff7654;

    text-decoration:
        none;

    font-size:
        10px;

    font-weight:
        800;

    transition:
        0.18s ease;
}


.discord-button:hover {

    background:
        rgba(255,70,20,0.12);

    color:
        #ff9a7e;
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
        rgba(255,255,255,0.05);

    color:
        #414145;

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
         DOWNLOAD / KEY
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

const downloadReady =
    {{ "true" if download_ready else "false" }};


/*
 * WICHTIG:
 *
 * Solange der Request noch nicht bestätigt wurde,
 * prüfen wir alle 2 Sekunden den Status.
 *
 * Sobald "approved" zurückkommt, wird die Seite
 * GENAU EINMAL neu geladen.
 *
 * Nach dem Reload ist downloadReady = true.
 * Dadurch wird dieses Script nicht mehr ausgeführt.
 */

if (
    requestId &&
    !downloadReady
) {

    let alreadyReloaded = false;


    const checkStatus = async () => {


        if (alreadyReloaded) {

            return;

        }


        try {


            const response =
                await fetch(
                    "/status/" +
                    encodeURIComponent(requestId),
                    {
                        cache:
                            "no-store"
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


                /*
                 * Verhindert mehrfaches Reloaden.
                 */

                alreadyReloaded =
                    true;


                /*
                 * Intervall stoppen.
                 */

                clearInterval(
                    statusInterval
                );


                /*
                 * Einmaliger Reload.
                 */

                window.location.reload();


            }


        } catch (error) {


            console.log(
                "Status check failed:",
                error
            );


        }

    };


    /*
     * Sofort einmal prüfen.
     */

    checkStatus();


    /*
     * Danach alle 2 Sekunden.
     */

    const statusInterval =
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

            message=
                "❌ Bitte gib einen Key ein."

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

            message=
                "❌ Dieser Key ist ungültig."

        )


    # --------------------------------------------------------
    # REQUEST ERSTELLEN
    # --------------------------------------------------------

    request_id = uuid.uuid4().hex


    PENDING_REQUESTS[request_id] = {

        "key":
            entered_key,

        "approved":
            False,

        "created":
            time.time()

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
            "DISCORD_WEBHOOK_URL "
            "ist nicht gesetzt."

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

                <title>
                    GENGA Admin
                </title>


                <style>

                    * {
                        box-sizing:
                            border-box;
                    }


                    body {

                        margin:0;

                        min-height:100vh;

                        display:flex;

                        align-items:center;

                        justify-content:center;

                        background:#070707;

                        color:white;

                        font-family:
                            Arial,
                            sans-serif;
                    }


                    .box {

                        width:350px;

                        padding:30px;

                        border-radius:11px;

                        background:#0d0d0f;

                        border:
                            1px solid
                            rgba(255,255,255,.08);

                        box-shadow:
                            0 20px 70px
                            rgba(0,0,0,.35);
                    }


                    .brand {

                        color:#ff5a2b;

                        font-size:10px;

                        font-weight:900;

                        letter-spacing:2px;

                        margin-bottom:10px;
                    }


                    h1 {

                        margin:
                            0 0 7px;

                        font-size:22px;
                    }


                    .description {

                        color:#69696f;

                        font-size:12px;

                        line-height:1.6;
                    }


                    .error {

                        margin-top:16px;

                        padding:10px;

                        border-radius:7px;

                        background:
                            rgba(255,70,20,.06);

                        border:
                            1px solid
                            rgba(255,70,20,.14);

                        color:#ff7553;

                        font-size:11px;
                    }


                    input {

                        width:100%;

                        height:42px;

                        padding:0 12px;

                        margin:
                            18px 0 9px;

                        border-radius:7px;

                        border:
                            1px solid
                            rgba(255,255,255,.08);

                        background:#070707;

                        color:white;

                        outline:none;
                    }


                    input:focus {

                        border-color:
                            rgba(255,70,20,.55);
                    }


                    button {

                        width:100%;

                        height:41px;

                        border:0;

                        border-radius:7px;

                        background:#ff461d;

                        color:white;

                        font-weight:850;

                        cursor:pointer;
                    }


                    button:hover {

                        background:#ff5728;
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

        <title>
            GENGA Admin
        </title>


        <style>

            * {
                box-sizing:
                    border-box;
            }


            body {

                margin:0;

                min-height:100vh;

                display:flex;

                align-items:center;

                justify-content:center;

                background:#070707;

                color:white;

                font-family:
                    Arial,
                    sans-serif;
            }


            .box {

                width:350px;

                padding:30px;

                border-radius:11px;

                background:#0d0d0f;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                box-shadow:
                    0 20px 70px
                    rgba(0,0,0,.35);
            }


            .brand {

                color:#ff5a2b;

                font-size:10px;

                font-weight:900;

                letter-spacing:2px;

                margin-bottom:10px;
            }


            h1 {

                margin:
                    0 0 7px;

                font-size:22px;
            }


            .description {

                color:#69696f;

                font-size:12px;

                line-height:1.6;
            }


            input {

                width:100%;

                height:42px;

                padding:0 12px;

                margin:
                    18px 0 9px;

                border-radius:7px;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                background:#070707;

                color:white;

                outline:none;
            }


            input:focus {

                border-color:
                    rgba(255,70,20,.55);
            }


            button {

                width:100%;

                height:41px;

                border:0;

                border-radius:7px;

                background:#ff461d;

                color:white;

                font-weight:850;

                cursor:pointer;
            }


            button:hover {

                background:#ff5728;
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


    if not PENDING_REQUESTS:


        requests_html = """

        <div class="empty">

            Keine Download-Anfragen vorhanden.

        </div>

        """


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

                padding:40px 20px;

                background:#070707;

                color:white;

                font-family:
                    Arial,
                    sans-serif;
            }}


            .container {{

                max-width:800px;

                margin:auto;
            }}


            .brand {{

                color:#ff5a2b;

                font-size:10px;

                font-weight:900;

                letter-spacing:2px;

                margin-bottom:10px;
            }}


            h1 {{

                margin:
                    0 0 8px;
            }}


            .subtitle {{

                color:#69696f;

                margin-bottom:30px;

                font-size:12px;
            }}


            .request {{

                padding:22px;

                margin-bottom:12px;

                background:#0d0d0f;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                border-radius:10px;
            }}


            .request p {{

                margin-top:18px;

                margin-bottom:6px;

                color:#999;

                font-size:11px;
            }}


            code {{

                display:block;

                padding:10px;

                border-radius:7px;

                background:#070707;

                color:#ff7048;

                word-break:break-all;

                font-family:
                    Consolas,
                    monospace;

                font-size:11px;
            }}


            .pending {{

                color:#ff9f43;

                font-size:11px;

                font-weight:bold;
            }}


            .approved {{

                color:#ff6841;

                font-size:11px;

                font-weight:bold;
            }}


            button {{

                margin-top:18px;

                padding:11px 16px;

                border:0;

                border-radius:7px;

                color:white;

                font-weight:bold;

                cursor:pointer;
            }}


            .approve {{

                background:#ff461d;
            }}


            .approve:hover {{

                background:#ff5728;
            }}


            .empty {{

                padding:25px;

                border-radius:10px;

                background:#0d0d0f;

                border:
                    1px solid
                    rgba(255,255,255,.08);

                color:#777;

                font-size:12px;
            }}


            .logout {{

                display:inline-block;

                margin-bottom:30px;

                color:#777;

                text-decoration:none;

                font-size:11px;
            }}


            .logout:hover {{

                color:white;
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


    if not data:

        return (
            "Download nicht freigegeben.",
            403
        )


    if not data["approved"]:

        return (
            "Dein Key wurde noch "
            "nicht bestätigt.",
            403
        )


    datei_pfad = os.path.join(

        os.path.dirname(
            os.path.abspath(__file__)
        ),

        DOWNLOAD_DATEI

    )


    if not os.path.isfile(
        datei_pfad
    ):

        return (
            "Download-Datei nicht gefunden.",
            404
        )


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
