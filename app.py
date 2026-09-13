from flask import Flask, redirect, render_template_string
app = Flask(__name__)
# ============================================================
# KONFIGURATION
# ============================================================
# Ziel des "Launch Client"-Buttons
GENGA_URL = "https://example.com"
# Genga Discord
DISCORD_URL = "https://discord.gg/VEEV2gaeB"
# ============================================================
# HTML + CSS
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
        /* ====================================================
           RESET
        ==================================================== */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        html {
            scroll-behavior: smooth;
        }
        /* ====================================================
           BODY
        ==================================================== */
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
        /* ====================================================
           BACKGROUND
        ==================================================== */
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
        /* ====================================================
           HEADER
        ==================================================== */
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
        /* ====================================================
           MAIN / HERO
        ==================================================== */
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
            box-shadow:
                0 0 30px
                rgba(124,58,237,0.08);
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
        /* ====================================================
           FEATURE CARDS
        ==================================================== */
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
        /* ====================================================
           DISCORD
        ==================================================== */
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
    <!-- ======================================================
         BACKGROUND
    ======================================================= -->
    <div class="background">
        <div class="grid"></div>
        <div class="glow glow-one"></div>
        <div class="glow glow-two"></div>
    </div>
    <!-- ======================================================
         HEADER
    ======================================================= -->
    <header>
        <div class="logo">
            GEN<span>GA</span>
        </div>
        <div class="status">
            <span class="status-dot"></span>
            SYSTEM ONLINE
        </div>
    </header>
    <!-- ======================================================
         MAIN
    ======================================================= -->
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
                Deine zentrale Anlaufstelle für den
                Genga Client. Modern, schnell und
                direkt erreichbar.
            </p>
            <!-- ==================================================
                 MAIN BUTTONS
            =================================================== -->
            <div class="buttons">
                <a
                    class="button primary"
                    href="/launch"
                >
                    Get GENGA-client&nbsp; →
                </a>
                <a
                    class="button secondary"
                    href="#features"
                >
                    Mehr erfahren
                </a>
            </div>
            <!-- ==================================================
                 FEATURES
            =================================================== -->
            <div
                class="features"
                id="features"
            >
                <!-- Feature 1 -->
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
                <!-- Feature 2 -->
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
                <!-- Discord -->
                <div class="card discord-card">
                    <div class="icon discord-icon">
                        <!-- Discord Logo -->
                        <svg
                            viewBox="0 0 24 24"
                            width="22"
                            height="22"
                            fill="currentColor"
                            aria-hidden="true"
                        >
                            <path
                                d="
                                M19.54 0
                                c1.14 0 2.06.92 2.06 2.06
                                v19.88
                                c0 1.14-.92 2.06-2.06 2.06
                                H4.46
                                C3.32 24 2.4 23.08 2.4 21.94
                                V2.06
                                C2.4.92 3.32 0 4.46 0
                                h15.08ZM8.1 7.08
                                a9.72 9.72 0 0 0-1.64 4.94
                                c1.18.88 2.33 1.4 3.48 1.4
                                l.83-1.03
                                a5.5 5.5 0 0 1-1.88-.63
                                l.46-.35
                                c1.14.54 2.3.81 3.46.81
                                s2.32-.27 3.46-.81
                                l.46.35
                                a5.5 5.5 0 0 1-1.88.63
                                l.83 1.03
                                c1.15 0 2.3-.52 3.48-1.4
                                A9.72 9.72 0 0 0 17.1 7.08
                                c-.64-.3-1.27-.52-1.88-.64
                                l-.24.47
                                c-.68-.1-1.36-.15-2.05-.15
                                s-1.37.05-2.05.15
                                l-.24-.47
                                c-.61.12-1.24.34-1.88.64ZM10.44 11.3
                                c-.42 0-.76-.39-.76-.87
                                s.34-.87.76-.87
                                .76.39.76.87
                                -.34.87-.76.87Zm3.12 0
                                c-.42 0-.76-.39-.76-.87
                                s.34-.87.76-.87
                                .76.39.76.87
                                -.34.87-.76.87Z
                                "
                            />
                        </svg>
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
                        href="https://discord.gg/VEEV2gaeB"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Discord beitreten →
                    </a>
                </div>
            </div>
        </section>
    </main>
    <!-- ======================================================
         FOOTER
    ======================================================= -->
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
    """
    Leitet den Launch-Button zum Genga Client weiter.
    Die URL steht oben in GENGA_URL.
    """
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
