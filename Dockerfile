FROM python:3.9-buster

# Install NGINX
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY deployment/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Build App
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG DJANGO_SETTINGS_MODULE
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
ARG DJANGO_ALLOWED_HOSTS
ENV DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS
ARG DEBUG
ENV DEBUG=$DEBUG
ARG AWS_S3_ACCESS_KEY_ID
ENV AWS_S3_ACCESS_KEY_ID=$AWS_S3_ACCESS_KEY_ID
ARG AWS_S3_SECRET_ACCESS_KEY
ENV AWS_S3_SECRET_ACCESS_KEY=$AWS_S3_SECRET_ACCESS_KEY
ARG GOOGLE_MAPS_API_KEY
ENV GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY
ARG POSTGRES_DB_NAME
ENV POSTGRES_DB_NAME=$POSTGRES_DB_NAME
ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/MyMemoryMaker
COPY . /opt/app/MyMemoryMaker
WORKDIR /opt/app/MyMemoryMaker
run echo $AWS_S3_ACCESS_KEY_ID
RUN pip install -r requirements/production.txt
RUN python manage.py collectstatic --no-input
RUN chown -R www-data:www-data /opt/app

# Start Server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/app/MyMemoryMaker/deployment/start_server.sh"]