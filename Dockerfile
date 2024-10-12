###############################################################################
# First stage: Build stage, do not copy application directory
FROM ghcr.io/pyvista/pyvista:latest-slim AS builder

# Install dependencies
COPY /app/requirements.txt .
RUN pip install -r requirements.txt --no-deps

# assume that the application directory is mounted to /app
CMD ["python", "/app/app.py"]

###############################################################################
# Second stage: Copy application directory
FROM builder

COPY /app /app

# Run the panel app on container startup
CMD ["python", "/app/app.py"]
