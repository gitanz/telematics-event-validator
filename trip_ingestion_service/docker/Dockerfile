FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=development

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install supervisor

# Only copy the src directory into the container
COPY ./src/ .

COPY docker/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 80

ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
