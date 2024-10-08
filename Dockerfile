FROM ghcr.io/pyvista/pyvista:latest-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

ENV APP_HOME=/app
ENV PORT=8080

# Copy local code to the container image.
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt --no-deps

# Run the web service on container startup.
CMD panel serve app/app.py --address 0.0.0.0 --port $PORT --allow-websocket-origin="*"