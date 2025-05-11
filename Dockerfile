FROM python:3.9-slim-buster

WORKDIR /app

COPY comm-server-2.py /app/

# Install any dependencies (in this case, none)
# RUN pip install --no-cache-dir -r requirements.txt

# No need to EXPOSE a port, Kubernetes uses the containerPort in the Deployment.
CMD ["python3", "comm-server-2.py"] # Do NOT hardcode the port here.