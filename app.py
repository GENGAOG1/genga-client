from flask import Flask, redirect, render_template_string

app = Flask(__name__)

# ============================================================
# KONFIGURATION
# ============================================================

# Später einfach durch deine echte Genga-Client-URL ersetzen.
GENGA_URL = "https://example.com"


# ============================================================
# HTML + CSS
# ============================================================

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

            color: white;

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

        /* ====================================================
           BACKGROUND
        ==================================================== */

        .background {
            position: fixed;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
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

            animation: gridMove 15s linear infinite;
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

        /* ====================================================
           HEADER
        ==================================================== */

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

            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 999px;

            background: rgba(255,255,255,0.04);
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

        /* ====================================================
           HERO
        ==================================================== */

        main {
            position: relative;
            z-index: 5;

            min-height: calc(100vh - 90px);

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

            border: 1px solid rgba(139,92,246,0.35);
            border-radius: 999px;

            background: rgba(139,92,246,0.08);

            color: #c4b5fd;

            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;

            box-shadow:
                0 0 30px rgba(124,58,237,0.08);
        }

        h1 {
            font-size: clamp(55px, 10vw, 115px);
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

        /* ====================================================
           BUTTONS
        ==================================================== */

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

            border: 1px solid rgba(255,255,255,0.12);

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
            color: #ddd;

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

        /* ====================================================
           FEATURES
        ==================================================== */

        .features {
            display: grid;
            grid-template-columns:
                repeat(3, 1fr);

            gap: 15px;

            max-width: 850px;

            margin: 75px auto 0;
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

        /* ====================================================
           FOOTER
        ==================================================== */

        footer {
            position: relative;
            z-index: 5;

            padding: 25px;

            text-align: center;

            color: #555560;
            font-size: 11px;
        }

        /* ====================================================
           MOBILE
        ==================================================== */

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

    <!-- Background -->
    <div class="background">
        <div class="grid"></div>
        <div class="glow glow-one"></div>
        <div class="glow glow-two"></div>
    </div>


    <!-- Header -->
    <header>

        <div class="logo">
            GEN<span>GA</span>
        </div>

        <div class="status">
            <span class="status-dot"></span>
            SYSTEM ONLINE
        </div>

    </header>


    <!-- Main -->
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
                Deine zentrale Anlaufstelle für den Genga Client.
                Modern, schnell und direkt erreichbar.
            </p>


            <div class="buttons">

                <!-- Dieser Button führt zu /launch -->
                <a
                    class="button primary"
                    href="/launch"
                >
                    Launch Client&nbsp; →
                </a>


                <a
                    class="button secondary"
                    href="#features"
                >
                    Mehr erfahren
                </a>

            </div>


            <!-- Features -->
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
                        Schneller und direkter Zugang
                        zu deinem Genga Client.
                    </p>

                </div>


                <div class="card">

                    <div class="icon">
                        ◈
                    </div>

                    <h3>
                        Modern Interface
                    </h3>

                    <p>
                        Ein modernes Dark-Interface
                        mit futuristischem Look.
                    </p>

                </div>


                <div class="card">

                    <div class="icon">
                        ◎
                    </div>

                    <h3>
                        Always Ready
                    </h3>

                    <p>
                        Deine Landingpage ist jederzeit
                        über Render erreichbar.
                    </p>

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
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/launch")
def launch():
    # Weiterleitung zum eigentlichen Genga Client
    return redirect(GENGA_URL)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
