### MWE - Panel + PyVista

This is a minimum working example of using PyVista/Trame with Panel. It's a
simple two tab single page app with:
- Tab 1 - PyVista Plotter Widget
- Tab 2 - Interactive sine wave

### Without Docker

```bash
pip install -r requirements.txt
make serve
```

Visit http://localhost:5006


### With Docker

```
make build
make serve-docker
```

Visit http://localhost:8080


### Issues

This application works because the trame port (5090) is exposed to the
host. This normally isn't an issue if you have control over the infrastructure
(e.g. private network or your own computer), but if you're deploying to [Google
Cloud](https://cloud.google.com/) with something like:

```
gcloud run services update panel-example --region us-central1 --min-instances=1
```

Google Cloud Run only exposes a single port, 8080, and all traffic to 5090 will
be blocked. You can simulate that by disabling the port mapping in docker
compose by commenting out `5090:5090` or `network_mode: 'host'`. Actually, the
port mapping `5090:5090` isn't really necessary here becuase the host network
mode exposes all ports; disabling host network mode causes this app to fail
when launched from docker even when exposing 5090.
