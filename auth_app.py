from flask import Flask, render_template_string, request, redirect, session, make_response
from Navi.models import db, User
from Navi.app import app as navi_app

# ----------------- Flask Setup -----------------
auth_app = Flask(__name__)
auth_app.secret_key = "super_secret_key"
auth_app.config["SESSION_COOKIE_NAME"] = "shared_session"
auth_app.config["SESSION_COOKIE_PATH"] = "/"   # ✅ Global cookie
auth_app.config["SESSION_COOKIE_DOMAIN"] = None
auth_app.config["SQLALCHEMY_DATABASE_URI"] = navi_app.config["SQLALCHEMY_DATABASE_URI"]
db.init_app(auth_app)

# -----------------  USER LOGIN/SIGNUP TEMPLATE -----------------
login_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>User Login / Signup</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html, body {
      height: 100%;
      width: 100%;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
      position: relative;
    }

    body::before {
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
    }

    @keyframes slide {
      0% { background-position: 0 0, 0 0; }
      100% { background-position: 70px 70px, -70px 70px; }
    }

    body::after {
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
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.8; }
    }

    .wrapper {
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }

    .auth-container {
      position: relative;
      width: 450px;
      animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(40px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .tab-switcher {
      display: flex;
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 6px;
      margin-bottom: 30px;
      border: 2px solid #334155;
      position: relative;
    }

    .tab-background {
      position: absolute;
      height: calc(100% - 12px);
      width: calc(50% - 6px);
      background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
      border-radius: 12px;
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      left: 6px;
      top: 6px;
      box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4);
    }

    .tab-background.signup {
      transform: translateX(calc(100% + 6px));
      background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
      box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4);
    }

    .tab-btn {
      flex: 1;
      padding: 14px 0;
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: color 0.3s ease;
      position: relative;
      z-index: 1;
    }

    .tab-btn.active {
      color: white;
    }

    .form-container {
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      padding: 50px 45px;
      border: 2px solid #334155;
      box-shadow: 
        0 25px 50px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(220, 38, 38, 0.2) inset;
      position: relative;
      overflow: hidden;
    }

    .form-container::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
      transition: left 0.5s;
    }

    .form-container:hover::before {
      left: 100%;
    }

    .form-content {
      display: none;
      animation: fadeIn 0.5s ease;
    }

    .form-content.active {
      display: block;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .title {
      font-size: 32px;
      font-weight: 700;
      color: #f1f5f9;
      margin-bottom: 10px;
      text-align: center;
    }

    .subtitle {
      font-size: 15px;
      color: #94a3b8;
      text-align: center;
      margin-bottom: 25px;
    }

    .input-group {
      margin-bottom: 20px;
      position: relative;
    }

    .input-label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      color: #cbd5e0;
      margin-bottom: 8px;
      margin-left: 4px;
    }

    .flip-card__input {
      width: 100%;
      height: 52px;
      border-radius: 12px;
      border: 2px solid #334155;
      background: #1e293b;
      font-size: 16px;
      font-weight: 500;
      color: #f1f5f9;
      padding: 0 20px;
      outline: none;
      transition: all 0.3s ease;
    }

    .flip-card__input:focus {
      border-color: #dc2626;
      background: #1e293b;
      box-shadow: 
        0 0 0 4px rgba(220, 38, 38, 0.2),
        0 0 20px rgba(220, 38, 38, 0.2);
    }

    .flip-card__input::placeholder {
      color: #475569;
    }

    .flip-card__btn {
      margin-top: 25px;
      width: 100%;
      height: 54px;
      border-radius: 12px;
      border: none;
      background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
      font-size: 17px;
      font-weight: 700;
      color: white;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 
        0 8px 25px rgba(220, 38, 38, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      position: relative;
      overflow: hidden;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .flip-card__btn:hover {
      transform: translateY(-3px);
      box-shadow: 
        0 12px 35px rgba(220, 38, 38, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .error-box {
      background: rgba(220, 38, 38, 0.15);
      border: 1px solid rgba(220, 38, 38, 0.5);
      color: #fca5a5;
      border-radius: 10px;
      padding: 12px 18px;
      font-size: 15px;
      font-weight: 600;
      margin-bottom: 20px;
      text-align: center;
      animation: shake 0.3s ease-in-out, fadeIn 0.5s ease;
      box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);
    }

    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-6px); }
      40%, 80% { transform: translateX(6px); }
    }

  </style>
</head>
<body>
  <div class="wrapper">
    <div class="auth-container">
      <div class="tab-switcher">
        <div class="tab-background" id="tabBackground"></div>
        <button class="tab-btn active" id="loginTab">Log in</button>
        <button class="tab-btn" id="signupTab">Sign up</button>
      </div>

      <div class="form-container">
        <!-- LOGIN FORM -->
        <div class="form-content active login-form" id="loginForm">
          <div class="title">Welcome Back</div>
          <div class="subtitle">Enter your credentials to continue</div>

          {% if error %}
          <div class="error-box">⚠️ {{ error }}</div>
          {% endif %}

          <form method="post" action="/auth/login">
            <div class="input-group">
              <label class="input-label">Username or Email</label>
              <input class="flip-card__input" name="username" placeholder="Enter your username" type="text" required>
            </div>
            <div class="input-group">
              <label class="input-label">Password</label>
              <input class="flip-card__input" name="password" placeholder="Enter your password" type="password" required>
            </div>
            <button class="flip-card__btn" type="submit">Sign In</button>
          </form>
        </div>

        <!-- SIGNUP FORM -->
        <div class="form-content signup-form" id="signupForm">
          <div class="title">Create Account</div>
          <div class="subtitle">Join us and start your journey</div>
          <form method="post" action="/auth/signup">
            <div class="input-group">
              <label class="input-label">Full Name</label>
              <input class="flip-card__input" name="name" placeholder="Enter your name" type="text" required>
            </div>
            <div class="input-group">
              <label class="input-label">Username or Email</label>
              <input class="flip-card__input" name="username" placeholder="Choose a username" type="text" required>
            </div>
            <div class="input-group">
              <label class="input-label">Password</label>
              <input class="flip-card__input" name="password" placeholder="Create a password" type="password" required>
            </div>
            <button class="flip-card__btn" type="submit">Create Account</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <script>
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const tabBackground = document.getElementById('tabBackground');

    function switchToLogin() {
      loginTab.classList.add('active');
      signupTab.classList.remove('active');
      loginForm.classList.add('active');
      signupForm.classList.remove('active');
      tabBackground.classList.remove('signup');
    }

    function switchToSignup() {
      signupTab.classList.add('active');
      loginTab.classList.remove('active');
      signupForm.classList.add('active');
      loginForm.classList.remove('active');
      tabBackground.classList.add('signup');
    }

    loginTab.addEventListener('click', switchToLogin);
    signupTab.addEventListener('click', switchToSignup);
  </script>
</body>
</html>
"""

# ----------------- ROUTES -----------------
@auth_app.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # 🚫 Prevent admin from logging in here
        if username.lower() == "admin":
            error = "Admins must log in via the Admin Portal."
            return render_template_string(login_page, error=error)

        user = User.query.filter_by(username=username).first()
        if not user:
            error = "Account not found. Please sign up first."
        elif not user.check_password(password):
            error = "Incorrect password. Try again."
        else:
            session["uid"] = user.id
            session["name"] = user.name
            session["username"] = user.username
            session["role"] = user.role
            resp = make_response(redirect("/"))
            resp.set_cookie(auth_app.config["SESSION_COOKIE_NAME"], session.get("_id", ""), path="/")
            return resp

    return render_template_string(login_page, error=error)


@auth_app.route("/signup", methods=["GET", "POST"])
def signup():
    """User Signup"""
    error = None
    if request.method == "POST":
        name = request.form["name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not name or not username or not password:
            error = "Please fill all fields."
        elif User.query.filter_by(username=username).first():
            error = "Username already exists. Try another."
        else:
            user = User(name=name, username=username, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect("/auth/login")

    return render_template_string(login_page, error=error)


@auth_app.route("/logout", endpoint="auth_logout")
def auth_logout():
    """Unified Logout Route"""
    session.clear()
    resp = make_response(redirect("/"))
    resp.set_cookie(auth_app.config["SESSION_COOKIE_NAME"], "", expires=0, path="/")
    return resp

@auth_app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Dedicated Admin Login Page"""
    PREDEFINED_ADMIN = {"username": "admin", "password": "admin123"}

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username == PREDEFINED_ADMIN["username"] and password == PREDEFINED_ADMIN["password"]:
            session["uid"] = 0
            session["username"] = username
            session["role"] = "admin"
            return redirect("/")

        return render_template_string("<h3 style='color:red;text-align:center;'>❌ Invalid admin credentials</h3><a href='/auth/admin'>Try again</a>")

    return render_template_string("""
   <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Portal - Secure Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            height: 100vh;
            overflow: hidden;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        body::before {
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
        }

        @keyframes slide {
            0% { background-position: 0 0, 0 0; }
            100% { background-position: 70px 70px, -70px 70px; }
        }

        body::after {
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
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .container {
            position: relative;
            z-index: 1;
            animation: slideIn 0.6s ease-out;
        }

        .login-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            padding: 50px 45px;
            border-radius: 20px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(99, 102, 241, 0.2) inset;
            width: 420px;
            max-width: 90vw;
        }

        .logo-container {
            text-align: center;
            margin-bottom: 35px;
            animation: float 3s ease-in-out infinite;
        }

        .logo {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
            border-radius: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin-bottom: 15px;
            box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4);
            position: relative;
        }

        h2 {
            color: #f1f5f9;
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 35px;
        }

        .input-group {
            position: relative;
            margin-bottom: 25px;
        }

        .input-group label {
            display: block;
            color: #cbd5e0;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            padding-left: 5px;
        }

        .input-wrapper {
            position: relative;
        }

        .input-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #64748b;
            font-size: 18px;
        }

        input {
            width: 100%;
            padding: 14px 15px 14px 45px;
            border: 2px solid #334155;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.3s ease;
            background: #1e293b;
            color: #f1f5f9;
            outline: none;
        }

        input:focus {
            border-color: #dc2626;
            box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
        }

        input::placeholder {
            color: #475569;
        }

        .remember-forgot {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-bottom: 25px;
            font-size: 13px;
        }

        .remember-me {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #cbd5e0;
            cursor: pointer;
        }

        .remember-me input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #dc2626;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
            position: relative;
            overflow: hidden;
        }

        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        button:hover::before {
            left: 100%;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(220, 38, 38, 0.5);
        }

        .back-link {
            text-align: center;
            margin-top: 25px;
        }

        .back-link a {
            color: #dc2626;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }

        .back-link a:hover {
            color: #ea580c;
            gap: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-card">
            <div class="logo-container">
                
                <h2>Admin Page</h2>
                <p class="subtitle">Administrative Access Control</p>
            </div>

            <form method="post">
                <div class="input-group">
                    <label for="username">Username</label>
                    <div class="input-wrapper">
                        <span class="input-icon">👤</span>
                        <input 
                            type="text" 
                            id="username" 
                            name="username" 
                            placeholder="Enter your username" 
                            required
                            autocomplete="username"
                        >
                    </div>
                </div>

                <div class="input-group">
                    <label for="password">Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input 
                            type="password" 
                            id="password" 
                            name="password" 
                            placeholder="Enter your password" 
                            required
                            autocomplete="current-password"
                        >
                    </div>
                </div>

                <div class="remember-forgot">
                    <label class="remember-me">
                        <input type="checkbox" name="remember" id="remember">
                        <span>Remember me</span>
                    </label>
                </div>

                <button type="submit">Access Control Panel</button>
            </form>

            <div class="back-link">
                <a href="/auth/select">← Back to authentication options</a>
            </div>
        </div>
    </div>
</body>
</html>

    """)


@auth_app.route("/select")
def select_role():
    """Page to choose between user or admin login."""
    return render_template_string("""
   <!DOCTYPE html>
<html>
<head>
    <title>Select Login Type</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            position: relative;
        }

        body::before {
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
        }

        @keyframes slide {
            0% { background-position: 0 0, 0 0; }
            100% { background-position: 70px 70px, -70px 70px; }
        }

        body::after {
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
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .container {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
            padding: 20px;
        }

        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 60px 50px;
            border: 2px solid #334155;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(220, 38, 38, 0.2) inset;
            max-width: 480px;
            width: 100%;
            animation: slideUp 0.6s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h2 {
            color: #f1f5f9;
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: #94a3b8;
            text-align: center;
            font-size: 16px;
            margin-bottom: 40px;
            font-weight: 400;
        }

        .button-group {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .btn {
            position: relative;
            background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
            color: white;
            border: none;
            padding: 18px 32px;
            border-radius: 12px;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(220, 38, 38, 0.5);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-icon {
            margin-right: 12px;
            font-size: 20px;
            display: inline-flex;
            align-items: center;
        }

        .btn:nth-child(2) {
            background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
        }

        .btn:nth-child(2):hover {
            box-shadow: 0 6px 25px rgba(220, 38, 38, 0.5);
        }

        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 24px 0;
            color: #64748b;
            font-size: 14px;
        }

        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #334155;
        }

        .divider span {
            padding: 0 16px;
            font-weight: 500;
        }

        @media (max-width: 480px) {
            .card {
                padding: 40px 30px;
            }
            
            h2 {
                font-size: 28px;
            }
            
            .btn {
                padding: 16px 28px;
                font-size: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>👋 Welcome Back</h2>
            <p class="subtitle">Choose your login type to continue</p>
            
            <div class="button-group">
                <a href="/auth/login" class="btn">
                    <span class="btn-icon">👤</span>
                    <span>Login as User</span>
                </a>
                
                <div class="divider"><span>or</span></div>
                
                <a href="/auth/admin" class="btn">
                    <span class="btn-icon">👨‍💼</span>
                    <span>Login as Admin</span>
                </a>
            </div>
        </div>
    </div>
</body>
</html>
    """)
