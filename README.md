### MWE - Panel + PyVista + Trame

This is a minimum working example of using PyVista/Trame with Panel. It's a
simple two tab single page app with:
- Tab 1 - PyVista Plotter Widget
- Tab 2 - Interactive sine wave

### Running the Application Locally

#### Without Docker

```bash
pip install -r app/requirements.txt
make serve
```

Visit http://localhost:8080


#### With Docker (dev)

```
make build
make serve-docker-dev
```

Visit http://localhost:8080


### Deploy on the cloud
