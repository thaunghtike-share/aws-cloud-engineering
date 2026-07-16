# Deploy Backend API on Amazon EC2 using Docker, Nginx & Certbot

## 1. Install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
newgrp docker
docker version
```

## 2. Create Docker Network

```bash
docker network create app-network
```

## 3. Create PostgreSQL Volume

```bash
docker volume create postgres-data
```

## 4. Run PostgreSQL Container

```bash
docker run -d \
  --name postgres \
  --restart unless-stopped \
  --network app-network \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppassword \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16
```

## 5. Verify PostgreSQL

```bash
docker ps
docker logs postgres
```

```bash
docker exec \
  -e PGPASSWORD=apppassword \
  postgres \
  psql -U appuser -d appdb -c "SELECT 1;"
```

## 6. Pull Backend Image

```bash
docker pull learndevopsnow123/flask-health-api:1.0
```

## 7. Run Backend Container

```bash
docker run -d \
  --name backend \
  --restart unless-stopped \
  --network app-network \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=appdb \
  -e DB_USER=appuser \
  -e DB_PASSWORD=apppassword \
  -p 8080:8080 \
  learndevopsnow123/flask-health-api:1.0
```

## 8. Verify Backend

```bash
docker ps
docker logs backend

curl -i http://localhost:8080/
curl -i http://localhost:8080/healthz

curl -i http://54.179.169.6:8080/
curl -i http://54.179.169.6:8080/healthz
```

## 9. Install Nginx

```bash
sudo apt update
sudo apt install -y nginx

sudo systemctl enable --now nginx
sudo systemctl status nginx --no-pager
```

## 10. Configure Cloudflare Wildcard DNS

Add a wildcard DNS record:

```text
Type: A
Name: *
IPv4 Address: EC2_ELASTIC_IP
Proxy Status: DNS only
TTL: Auto
```

The wildcard record supports subdomains such as:

```text
api.learndevopsnow.it.com
portal.learndevopsnow.it.com
admin.learndevopsnow.it.com
```

## 11. Verify DNS

```bash
dig +short api.learndevopsnow.it.com
```

```bash
nslookup api.learndevopsnow.it.com
```

## 12. Configure Backend Nginx Site

```bash
sudo tee /etc/nginx/sites-available/api.learndevopsnow.it.com >/dev/null <<'EOF'
server {
    listen 80;
    listen [::]:80;

    server_name api.learndevopsnow.it.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

## 13. Enable Backend Nginx Site

```bash
sudo ln -sf \
  /etc/nginx/sites-available/api.learndevopsnow.it.com \
  /etc/nginx/sites-enabled/api.learndevopsnow.it.com
```

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 14. Verify Backend Domain

```bash
curl -i http://api.learndevopsnow.it.com
```

## 15. Install Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

## 16. Enable Backend HTTPS

```bash
sudo certbot --nginx -d api.learndevopsnow.it.com
```

```bash
sudo certbot certificates
```

```bash
curl -i https://api.learndevopsnow.it.com
```
