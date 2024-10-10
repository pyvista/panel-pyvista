###############################################################################
# First stage: Build stage
FROM ghcr.io/pyvista/pyvista:latest-slim AS builder

# Install dependencies
COPY /app/requirements.txt .
RUN pip install -r requirements.txt --no-deps

CMD ["python", "/app/app.py"]

###############################################################################
# Second stage: Final stage for a slimmer production image
FROM ghcr.io/pyvista/pyvista:latest-slim

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.*/site-packages /usr/local/lib/python3.*/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True
ENV APP_PORT=8080

# Copy application directory only
COPY /app /app

# Run the panel app on container startup
CMD ["python", "/app/app.py"]
