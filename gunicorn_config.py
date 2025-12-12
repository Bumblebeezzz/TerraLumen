"""
Gunicorn configuration for Render deployment
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
# Use fewer workers on Render to avoid memory issues
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'terralumen'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (not needed on Render)
keyfile = None
certfile = None
