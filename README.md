### MWE - Panel + PyVista + Trame

![App Screenshot](./app-sc.png)

This is minimum working example of using [PyVista](https://docs.pyvista.org/) & [Trame](https://kitware.github.io/trame/) with [Panel](https://panel.holoviz.org/). It's designed to be able to be deployed on the cloud (e.g. [GCP](https://cloud.google.com/)) via a [Docker](https://www.docker.com/) image and only using port 8080.

Normally, Trame requires you to open up a second port in addition to the default to the Panel port, but here we use [jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy) to proxy the traffic to an endpoint of our choosing, in this case, `/proxy`. This way, we can get the benefits of using the Trame with PyVista and being able to deploy on the cloud.

While, Panel already has a [VTK](https://panel.holoviz.org/reference/panes/VTK.html) extension, it uses an old serializer.


### Running the Application Locally

#### Without Docker

```bash
pip install -r app/requirements.txt
make serve
```

Visit http://localhost:8080


#### With Docker Compose

```
make build
make serve-docker
```

Visit http://localhost:8080


### Deploy on the cloud

