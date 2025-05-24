#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "⚠️  Please run as root: sudo $0 <GIT_REPO_URL> [SERVER_NAME]"
  exit 1
fi

REPO_URL="$1"
SERVER_NAME="${2:-_}"
APP_DIR="/opt/hotwheels_app"
SERVICE_FILE="/etc/systemd/system/hotwheels.service"
NGINX_CONF="/etc/nginx/sites-available/hotwheels"

echo "📦 Updating apt and installing dependencies..."
apt update && apt upgrade -y
apt install -y python3-venv python3-pip git nginx

echo "🔀 Cloning your app into ${APP_DIR}..."
rm -rf "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"
chown -R pi:pi "$APP_DIR"

echo "🐍 Setting up Python venv and installing requirements..."
cd "$APP_DIR"
sudo -u pi python3 -m venv venv
sudo -u pi bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt gunicorn"

echo "⚙️  Creating systemd service..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Hot Wheels Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd and starting hotwheels service..."
systemctl daemon-reload
systemctl enable hotwheels
systemctl restart hotwheels

echo "🕸️  Configuring Nginx reverse proxy..."
cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name ${SERVER_NAME};

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
    }
}
EOF

ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/hotwheels
nginx -t
systemctl restart nginx

echo "✅ Installation complete!"
echo "• App URL: http://<your_pi_IP_or_domain>/"
echo "• View logs: sudo journalctl -u hotwheels -f"
