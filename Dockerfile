# Simple Dockerfile for Django (development/demo)
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN apt-get update \
	&& apt-get install -y --no-install-recommends nodejs npm \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& pip install --no-cache-dir -r requirements.txt
COPY . /app/
# DO NOT run collectstatic during image build. Running collectstatic at start (or pre-deploy)
# is safer when static storage requires runtime environment (S3 credentials, DATABASE_URL, etc.).
# Bind to the PORT environment variable provided by the platform
CMD ["sh", "-c", "gunicorn lawyer_site.wsgi:application --bind 0.0.0.0:$PORT"]
