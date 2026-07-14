# AWS EC2 Basic Lab Commands

## 1. SSH Login to EC2 Instance

Change Private Key permission:

```bash
chmod 400 <key-file>.pem
```

Login to EC2 Ubuntu Server:

```bash
ssh -i <key-file>.pem ubuntu@<public-ip>
```

Example:

```bash
ssh -i aws-lab.pem ubuntu@54.xx.xx.xx
```

---

## 2. Update Package Repository

Update Ubuntu package list:

```bash
sudo apt update
```

---

## 3. Install NGINX Web Server

Install NGINX:

```bash
sudo apt install nginx -y
```

---

## 4. Check NGINX Service Status

Check NGINX service:

```bash
sudo systemctl status nginx
```

---

## 5. Start NGINX Service

Start NGINX:

```bash
sudo systemctl start nginx
```

---

## 6. Enable NGINX Service

Enable NGINX to start automatically after reboot:

```bash
sudo systemctl enable nginx
```

---

## 7. Restart NGINX Service

Restart NGINX:

```bash
sudo systemctl restart nginx
```

---

## 8. Access NGINX Web Server

After allowing HTTP Port 80 in Security Group:

Open browser:

```text
http://<EC2-Public-IP>
```

You should see:

```text
NGINX Welcome Page
```

---

## 9. Logout from EC2 Server

Exit SSH session:

```bash
exit
```

---

## EC2 Lab Cleanup

After finishing the lab:

Terminate the EC2 Instance to avoid unnecessary AWS charges.