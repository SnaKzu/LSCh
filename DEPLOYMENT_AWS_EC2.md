# 🏗️ Despliegue en AWS EC2 - LSCh Recognition

## ¿Cuándo elegir EC2?
- ✅ **Control total del servidor**
- ✅ **Personalización completa**
- ✅ **Mejor para aplicaciones complejas**
- ❌ **Más costoso** ($15-30/mes mínimo)
- ❌ **Requiere conocimiento DevOps**
- ❌ **Más tiempo de configuración**

## Costos Estimados AWS
```
EC2 t3.micro (1 vCPU, 1GB RAM): ~$8.50/mes
EC2 t3.small (2 vCPU, 2GB RAM): ~$17/mes
Elastic IP: ~$3.65/mes
EBS Storage (20GB): ~$2/mes
Total: ~$15-25/mes
```

## Preparación Local

### 1. Archivos de configuración

#### `docker-compose.yml`
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///app/lsp_users.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - web
    restart: unless-stopped
```

#### `Dockerfile`
```dockerfile
FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs data

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

#### `nginx.conf`
```nginx
events {
    worker_connections 1024;
}

http {
    upstream lsch_app {
        server web:5000;
    }

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name _;

        ssl_certificate /etc/ssl/cert.pem;
        ssl_certificate_key /etc/ssl/key.pem;

        location / {
            proxy_pass http://lsch_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /socket.io/ {
            proxy_pass http://lsch_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

## Pasos Despliegue EC2

### 1. Crear instancia EC2

```bash
# 1. Ir a AWS Console → EC2
# 2. Launch Instance
# 3. Seleccionar Ubuntu 22.04 LTS
# 4. Tipo: t3.small (recomendado para ML)
# 5. Crear Key Pair: lsch-keypair.pem
# 6. Security Group:
#    - SSH (22): Tu IP
#    - HTTP (80): 0.0.0.0/0
#    - HTTPS (443): 0.0.0.0/0
#    - Custom (5000): 0.0.0.0/0
```

### 2. Conectar a la instancia

```bash
# Cambiar permisos de la key
chmod 400 lsch-keypair.pem

# Conectar por SSH
ssh -i lsch-keypair.pem ubuntu@tu-ip-publica-ec2
```

### 3. Configurar servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo systemctl enable docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
sudo apt install git -y

# Cerrar sesión y volver a conectar
exit
ssh -i lsch-keypair.pem ubuntu@tu-ip-publica-ec2
```

### 4. Clonar y configurar proyecto

```bash
# Clonar proyecto
git clone https://github.com/tu-usuario/lsch-recognition.git
cd lsch-recognition

# Crear archivos de configuración
nano .env
```

#### Contenido `.env`
```env
FLASK_ENV=production
SECRET_KEY=tu-clave-super-secreta-production
DATABASE_URL=sqlite:///app/data/lsp_users.db
CONFIDENCE_THRESHOLD=0.7
DEBUG=False
```

### 5. Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot

# Generar certificados (reemplaza tu-dominio.com)
sudo certbot certonly --standalone -d tu-dominio.com

# Copiar certificados
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem
sudo chown ubuntu:ubuntu ssl/*
```

### 6. Construir y ejecutar

```bash
# Construir imagen Docker
docker-compose build

# Ejecutar aplicación
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 7. Configurar dominio (Opcional)

#### En tu proveedor de dominio (GoDaddy, Namecheap, etc.):
```
Tipo: A Record
Nombre: @
Valor: IP-PUBLICA-DE-TU-EC2
TTL: 300
```

### 8. Monitoreo y mantenimiento

```bash
# Ver estado de contenedores
docker-compose ps

# Reiniciar aplicación
docker-compose restart

# Actualizar código
git pull
docker-compose build
docker-compose up -d

# Backup de base de datos
docker-compose exec web python -c "
import sqlite3
import shutil
shutil.copy('data/lsp_users.db', 'data/backup_$(date +%Y%m%d).db')
"

# Ver uso de recursos
htop
df -h
docker stats
```

### 9. Automatizar renovación SSL

```bash
# Crear script de renovación
sudo nano /etc/cron.d/certbot-renew

# Contenido:
0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook "cd /home/ubuntu/lsch-recognition && docker-compose restart nginx"
```

## Estructura Final EC2
```
/home/ubuntu/lsch-recognition/
├── web-app/
├── models/
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── .env
├── ssl/
│   ├── cert.pem
│   └── key.pem
├── data/
│   └── lsp_users.db
└── logs/
```

## Comandos útiles EC2
```bash
# Monitoreo
docker-compose logs -f web
sudo systemctl status docker
free -h
df -h

# Backup automático
0 2 * * * cd /home/ubuntu/lsch-recognition && docker-compose exec -T web python backup.py

# Actualización automática
0 4 * * 1 cd /home/ubuntu/lsch-recognition && git pull && docker-compose build && docker-compose up -d
```

## Ventajas EC2
✅ Control total del servidor  
✅ Personalización completa  
✅ Mejores recursos para ML  
✅ Múltiples aplicaciones  
✅ Base de datos dedicada  

## Desventajas EC2
❌ Más costoso ($15-30/mes)  
❌ Configuración compleja  
❌ Mantenimiento manual  
❌ Requiere conocimiento DevOps  
❌ SSL manual  