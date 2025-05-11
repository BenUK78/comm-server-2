FROM python:3.9-slim-buster

WORKDIR /app

COPY comm-server-2.py /app/

# Install any dependencies (in this case, none)
# RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002
#  No longer hardcoded, the application listens on the port it receives from here.
CMD ["python3", "comm-server-2.py", "8002"]