import os
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM = """
<!doctype html>
<title>Astrologer Bot Installer</title>
<h1>Astrologer Bot Web Installer</h1>
<form method=post>
  <label>Telegram Bot Token:<br><input name=TELEGRAM_BOT_TOKEN required></label><br>
  <label>Webhook URL:<br><input name=TELEGRAM_WEBHOOK_URL></label><br>
  <label>OpenRouter API Key:<br><input name=OPENROUTER_API_KEY required></label><br>
  <label>Payments Token:<br><input name=TELEGRAM_PAYMENTS_TOKEN></label><br>
  <label>Yookassa Shop ID:<br><input name=YOOKASSA_SHOP_ID></label><br>
  <label>Yookassa Secret:<br><input name=YOOKASSA_SECRET_KEY></label><br>
  <label>Admin Username:<br><input name=ADMIN_USERNAME value="admin"></label><br>
  <label>Admin Password:<br><input name=ADMIN_PASSWORD value="admin"></label><br>
  <button type=submit>Install</button>
</form>
"""

SUCCESS = """
<!doctype html>
<title>Installed</title>
<h1>Installation complete</h1>
<p>The bot is starting. You can close this window.</p>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        values = {k: request.form.get(k, '') for k in request.form}
        env_path = os.path.join('backend', '.env')
        # Fill from example and override with user values
        with open(os.path.join('backend', '.env.example')) as f:
            lines = []
            for line in f:
                if line.strip() == '' or line.startswith('#'):
                    lines.append(line)
                    continue
                key = line.split('=', 1)[0]
                if key in values and values[key]:
                    lines.append(f"{key}={values[key]}\n")
                else:
                    lines.append(line)
        with open(env_path, 'w') as f:
            f.writelines(lines)
        # Save postgres password
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('DATABASE_URL'):
                    pwd = line.split(':')[2].split('@')[0]
                    f.write(f"POSTGRES_PASSWORD={pwd}\n")
                    break
        subprocess.Popen(['docker-compose', '--profile', 'production', 'up', '-d'])
        return SUCCESS
    return render_template_string(FORM)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
