import subprocess
import time
from flask import Flask, render_template_string, session
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from Navi.app import app as navi_app
from auth_app import auth_app
from chatbot.app_backend import app as chatbot_app
from FakeNews.app import app as fake_app
import session_config


# ---------------- Launch Chatbot Backend ----------------
def launch_chatbot_backend():
    print("🚀 Launching Chatbot backend on port 5000...")
    process = subprocess.Popen(["python", "-m", "chatbot.app_backend"])
    time.sleep(3)
    return process


# ---------------- Launch Fake News Backend ----------------
def launch_fakenews_backend():
    print("📰 Launching Fake News Detection backend on port 7000...")
    process = subprocess.Popen(["python", "-m", "FakeNews.app"])
    time.sleep(3)
    return process


# ---------------- Main Flask App ----------------
landing_app = Flask(__name__)
landing_app.config.from_object(session_config)
landing_app.secret_key = session_config.SECRET_KEY


@landing_app.route("/")
def home():
    """Landing page for Integrated Safety Application"""
    logged_in = "uid" in session
    username = session.get("username", "User")
    name = session.get("name", "User")
    role = session.get("role", None)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Welcome | Integrated Safety System</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
            overflow-x: hidden;
            font-family: 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            position: relative;
            color: #fff;
        }}

        /* Animated diagonal grid pattern */
        body::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(220, 38, 38, 0.03) 35px, rgba(220, 38, 38, 0.03) 70px),
                repeating-linear-gradient(-45deg, transparent, transparent 35px, rgba(234, 179, 8, 0.03) 35px, rgba(234, 179, 8, 0.03) 70px);
            animation: slide 20s linear infinite;
            z-index: 0;
        }}

        @keyframes slide {{
            0% {{ background-position: 0 0, 0 0; }}
            100% {{ background-position: 70px 70px, -70px 70px; }}
        }}

        /* Radial light glow */
        body::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 15% 20%, rgba(220, 38, 38, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(234, 179, 8, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(239, 68, 68, 0.05) 0%, transparent 60%);
            animation: pulse 8s ease-in-out infinite;
            z-index: 0;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}

        body > * {{
            position: relative;
            z-index: 2;
        }}

        h1,h4 {{
            font-size: 2.2em;
            color: #f1f5f9;
            margin-top: 40px;
            margin-bottom: 30px;
            text-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            animation: fadeInDown 0.8s ease-out;
            text-align: center;
            font-weight: 600;
            letter-spacing: -0.5px;
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        p {{
            font-size: 1.2em;
            color: #cbd5e0;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}

        /* 🔸 Scrolling Message Bar */
        .scroll-bar {{
            width: 100%;
            color: #fff;
            padding: 10px 0;
            font-size: 16px;
            font-weight: 600;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            position: sticky;
            top: 0;
            z-index: 100;
            margin-bottom: 40px;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(6px);
        }}

        .scroll-bar marquee {{
            font-family: "Segoe UI", sans-serif;
            letter-spacing: 0.5px;
        }}

        /* Buttons */
        .continue-btn {{
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 12px;
            background: linear-gradient(135deg, #dc2626, #ea580c);
            box-shadow: 0px 10px 30px 0px rgba(220, 38, 38, 0.4);
            cursor: pointer;
            border: none;
            text-decoration: none;
            width: 220px;
            margin: 0 auto;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .continue-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0px 15px 40px 0px rgba(220, 38, 38, 0.5);
        }}

        .continue-btn span {{
            width: 100%;
            padding: 18px 25px;
            color: #fff;
            font-size: 1.125em;
            font-weight: 700;
            letter-spacing: 0.3em;
            z-index: 20;
        }}

        .btn {{
            display: inline-block;
            padding: 14px 28px;
            margin: 12px;
            text-decoration: none;
            border-radius: 10px;
            font-size: 1.1em;
            color: white;
            font-weight: 600;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}

        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }}

        .btn-green, .btn-orange {{
            background: linear-gradient(135deg, #dc2626, #ea580c);
        }}

        .btn-green:hover, .btn-orange:hover {{
            background: linear-gradient(135deg, #b91c1c, #dc2626);
        }}

        .btn-logout {{
            background: linear-gradient(135deg, #dc2626, #ef4444);
        }}
        .btn-logout:hover {{
            background: linear-gradient(135deg, #b91c1c, #dc2626);
        }}

        /* ✅ Center buttons */
        .btn-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-top: 20px;
            margin-bottom: 30px;
        }}

        .logout-container {{
            display: flex;
            justify-content: center;
        }}

        /* Chatbot Widget */
        .chatbot-widget {{
            position: fixed;
            bottom: 90px;
            right: 30px;
            width: 400px;
            height: 520px;
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
            overflow: hidden;
            background: #1e293b;
            border: 2px solid rgba(220, 38, 38, 0.5);
            display: none;
            z-index: 1000;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 20px;
        }}

        .chatbot-toggle {{
            position: fixed;
            bottom: 25px;
            right: 30px;
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: linear-gradient(135deg, #dc2626, #ea580c);
            box-shadow: 0 8px 25px rgba(220, 38, 38, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 30px;
            cursor: pointer;
            z-index: 1100;
            transition: all 0.3s ease;
        }}

        .chatbot-toggle:hover {{
            background: linear-gradient(135deg, #b91c1c, #dc2626);
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 12px 35px rgba(220, 38, 38, 0.7);
        }}
    </style>
</head>
<body>
<h1>ResQnet<h1>
    <h4>🌐 A Multi-Module Disaster Management Application integrating Navigation, Fake News Detection, and Multilingual Chatbot</h4>

   
    """

    # --- NOT LOGGED IN ---
    if not logged_in:
        html += """
         <div class="scroll-bar">
      <marquee behavior="scroll" direction="left" scrollamount="6">
        ⚠️ Stay informed during disasters | 📰 Verify news before sharing | 💬 Chat with your Offline Assistant | 🏠 Locate Safehouses instantly | 🌎 Empower your community with technology
      </marquee>
      </div>
       <p>Please continue to sign in or register to access the application.</p>
        <a href="/auth/select" class="continue-btn"><span>CONTINUE</span></a>
        """

    # --- USER ---
    elif role == "user":
        html += f"""
        <p>Welcome back, <strong>{name}</strong>!</p>
        <div class="btn-container">
            <a href="/navi/map" class="btn btn-green">🗺️ Navigator</a>
            <a href="/fakenews" class="btn btn-orange">📰 Fake News Detector</a>
        </div>
        <div class="logout-container">
            <a href="/auth/logout" class="btn btn-logout">🚪 Logout</a>
        </div>

        <div class="chatbot-widget" id="chatbot-box">
            <iframe src="/chatbot"></iframe>
        </div>
        <div class="chatbot-toggle" id="chatbot-btn">💬</div>

        <script>
            const btn = document.getElementById("chatbot-btn");
            const box = document.getElementById("chatbot-box");
            let visible = false;

            btn.addEventListener("click", () => {{
                visible = !visible;
                box.style.display = visible ? "block" : "none";
                btn.textContent = visible ? "✖" : "💬";
            }});
        </script>
        """

    # --- ADMIN ---
    elif role == "admin":
        html += f"""
        <p>Welcome back, <strong>{username}</strong> (Admin)!</p>
        <div class="btn-container">
            <a href="/navi/admin" class="btn btn-green">🛠️ Admin Dashboard</a>
        </div>
        <div class="logout-container">
            <a href="/auth/logout" class="btn btn-logout">🚪 Logout</a>
        </div>
        """

    html += """
</body>
</html>
"""
    return render_template_string(html)


# ---------------- Dispatcher Middleware ----------------
application = DispatcherMiddleware(
    landing_app,
    {
        "/auth": auth_app,
        "/navi": navi_app,
        "/chatbot": chatbot_app,
        "/fakenews": fake_app,
    },
)


# ---------------- Run Combined App ----------------
if __name__ == "__main__":
    chatbot_proc = launch_chatbot_backend()
    fakenews_proc = launch_fakenews_backend()
    try:
        print("🌍 Combined Flask Application running on http://127.0.0.1:8000")
        run_simple("127.0.0.1", 8000, application, use_debugger=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backends...")
        chatbot_proc.terminate()
        fakenews_proc.terminate()
        chatbot_proc.wait()
        fakenews_proc.wait()
        print("✅ All services stopped cleanly.")
