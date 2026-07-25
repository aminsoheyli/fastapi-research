# Systemd deployment

This directory contains the production service unit for the FastAPI app.

## Install

```bash
sudo cp deploy/systemd/social-api.service /etc/systemd/system/social-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now social-api.service
```

## Check status

```bash
sudo systemctl status social-api.service
sudo journalctl -u social-api.service -f
```

## Restart

```bash
sudo systemctl restart social-api.service
```

## Notes

- Update `ExecStart` if your ASGI app module path is not `app.main:app`.
- Update `User`, `Group`, `WorkingDirectory`, and `PATH` to match your host environment.
- If running behind a reverse proxy, keep binding on `127.0.0.1:8000`.
