# Startup Scripts

This folder contains various scripts to start the Resume Parser application.

## Available Scripts

### Python Scripts

- **`simple_start.py`** - Simple server startup (recommended for development)
- **`fast_start.py`** - Fast server startup with minimal dependencies
- **`start_server.py`** - Standard server startup script
- **`run_local.py`** - Run server locally

### Shell Scripts

- **`start_server.sh`** - Linux/Mac startup script
- **`start_server.bat`** - Windows startup script

## Usage

### Recommended (Development)

```bash
python scripts/startup/simple_start.py
```

### Windows

```batch
scripts\startup\start_server.bat
```

### Linux/Mac

```bash
chmod +x scripts/startup/start_server.sh
./scripts/startup/start_server.sh
```

The server will start on `http://localhost:8000`

