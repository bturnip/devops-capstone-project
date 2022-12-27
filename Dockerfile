FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

#--copy service package
COPY service/ ./service/

#--create theia user and give ownership of app folder
RUN useradd --uid 1000
RUN chown -R theia /app
USER theia

#--open the port and run the service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]