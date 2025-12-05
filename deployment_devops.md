# Plan Deployment DevOps: MCP LPDP Pencairan

## Objective
Membuat workflow GitHub Actions untuk auto-deploy aplikasi MCP Server ke dev server lokal via SSH dengan Docker Registry.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   GitHub Repo   │────▶│  GitHub Actions  │────▶│  Docker Registry│
│  (Push/PR)      │     │  (Build & Push)  │     │  (GHCR/DockerHub)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   Dev Server    │
                                                 │  (via SSH)      │
                                                 │  docker pull &  │
                                                 │  docker run     │
                                                 └─────────────────┘
```

---

## Workflow Triggers

| Event | Branch | Action |
|-------|--------|--------|
| `push` | `main` | Build, Push to Registry, Deploy to Dev |
| `pull_request` | `main` | Build & Test only (no deploy) |
| `push` | `develop` | Build, Push to Registry, Deploy to Dev |

---

## Tech Stack

- **Container Registry**: GitHub Container Registry (ghcr.io) - gratis untuk repo publik/privat
- **Docker**: Multi-stage build untuk image yang lebih kecil
- **SSH**: Untuk remote deployment ke dev server
- **Secrets Management**: GitHub Secrets untuk credentials

---

## GitHub Secrets yang Diperlukan

| Secret Name | Value | Deskripsi |
|-------------|-------|-----------|
| `DEV_SERVER_HOST` | `103.164.191.212` | IP dev server |
| `DEV_SERVER_USER` | `devjc` | Username SSH |
| `DEV_SERVER_SSH_KEY` | *(isi dari devops02.ppk converted to OpenSSH)* | Private SSH key |
| `DEV_SERVER_PORT` | `22193` | Port SSH |
| `GOOGLE_API_KEY` | *(dari .env)* | API key Gemini |
| `PINECONE_API_KEY` | *(dari .env)* | API key Pinecone |

### Konfigurasi SSH
- **Host**: 103.164.191.212
- **Port**: 22193
- **Username**: devjc
- **Key File**: devops02.ppk (perlu dikonversi ke OpenSSH format)

> ⚠️ **Penting**: File `.ppk` adalah format PuTTY. Perlu dikonversi ke OpenSSH format menggunakan:
> ```bash
> # Di Linux/Mac dengan puttygen
> puttygen devops02.ppk -O private-openssh -o devops02_openssh.key
> ```
> Kemudian isi `DEV_SERVER_SSH_KEY` dengan konten file `devops02_openssh.key`

---

## File yang Akan Dibuat

### 1. `Dockerfile`
```dockerfile
# Multi-stage build untuk Python MCP Server
FROM python:3.11-slim as builder
# Install dependencies
# Copy source code

FROM python:3.11-slim as runtime
# Copy dari builder
# Set environment variables
# Run MCP server
```

### 2. `docker-compose.yml`
```yaml
# Untuk deployment di dev server
services:
  lpdp-mcp:
    image: ghcr.io/adityaldy/lpdp-mcp:latest
    environment:
      - GOOGLE_API_KEY
      - PINECONE_API_KEY
    restart: unless-stopped
```

### 3. `.github/workflows/deploy-dev.yml`
```yaml
name: Deploy to Dev Server

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    # Build Docker image
    # Push ke GHCR
    
  deploy:
    # SSH ke dev server
    # Pull image terbaru
    # Restart container
```

### 4. `.dockerignore`
```
venv/
__pycache__/
*.pyc
.env
.git/
docs/
tests/
```

---

## Workflow Steps Detail

### Job 1: Build & Push

```yaml
steps:
  1. Checkout code
  2. Setup Docker Buildx
  3. Login to GitHub Container Registry
  4. Build Docker image with tags:
     - ghcr.io/adityaldy/lpdp-mcp:latest
     - ghcr.io/adityaldy/lpdp-mcp:<sha>
  5. Push to registry
```

### Job 2: Deploy (hanya untuk push, bukan PR)

```yaml
steps:
  1. SSH ke dev server (103.164.191.212:22193)
  2. docker pull ghcr.io/adityaldy/lpdp-mcp:latest
  3. docker-compose down (stop existing)
  4. docker-compose up -d (start new)
  5. Health check
  6. Cleanup old images
```

---

## Security Considerations

1. **SSH Key**: Gunakan Ed25519 atau RSA 4096-bit
2. **Least Privilege**: User SSH hanya punya akses docker
3. **Network**: Dev server di belakang firewall, hanya SSH yang terbuka
4. **Secrets**: Tidak ada credentials di code, semua via GitHub Secrets
5. **Image Signing**: Optional - gunakan cosign untuk verify image

---

## Dev Server Requirements

- Docker Engine 20.10+
- Docker Compose v2
- SSH access dengan key authentication
- Port 22 terbuka untuk GitHub Actions IP ranges
- Storage minimal 5GB untuk Docker images

---

## Deployment Flow

```
1. Developer push ke main/develop
         │
         ▼
2. GitHub Actions triggered
         │
         ▼
3. Build Docker image
         │
         ▼
4. Push ke ghcr.io
         │
         ▼
5. SSH ke dev server
         │
         ▼
6. Pull image terbaru
         │
         ▼
7. Restart container dengan docker-compose
         │
         ▼
8. Health check & notification
```

---

## Rollback Strategy

Jika deployment gagal:
1. Image sebelumnya tetap ada di registry dengan tag SHA
2. Manual rollback: `docker pull ghcr.io/adityaldy/lpdp-mcp:<previous-sha>`
3. Atau revert commit di GitHub, trigger redeploy

---

## Monitoring & Logging

- Docker logs: `docker logs lpdp-mcp`
- Container status: Health check endpoint (optional)
- GitHub Actions: Build/deploy status di PR/commit

---

## Estimasi File Changes

| File | Action | Deskripsi |
|------|--------|-----------|
| `Dockerfile` | Create | Multi-stage build untuk MCP server |
| `docker-compose.yml` | Create | Orchestration untuk dev server |
| `.dockerignore` | Create | Exclude files dari Docker build |
| `.github/workflows/deploy-dev.yml` | Create | CI/CD workflow |
| `.github/workflows/deploy.yml` | Update/Remove | Workflow lama (jika ada) |

---

## Timeline Implementasi

1. **Setup (5 menit)**
   - Buat Dockerfile
   - Buat docker-compose.yml
   - Buat .dockerignore

2. **GitHub Actions (5 menit)**
   - Buat workflow deploy-dev.yml
   - Setup secrets (manual oleh user)

3. **Testing (5 menit)**
   - Test local Docker build
   - Verify workflow syntax

---

## Approval Checklist

Sebelum implementasi, mohon konfirmasi:

- [x] Registry: GitHub Container Registry (ghcr.io/adityaldy)
- [x] Branch: Trigger pada `main` dan `develop`
- [x] SSH Config: 103.164.191.212:22193 (user: devjc)
- [ ] SSH Key: devops02.ppk sudah dikonversi ke OpenSSH format?
- [ ] Dev Server: Docker & Docker Compose sudah terinstall?
- [ ] GitHub Secrets: Sudah di-setup di repository?

---

**Status: MENUNGGU APPROVAL**

Silakan review plan di atas dan konfirmasi jika sudah OK untuk implementasi.
