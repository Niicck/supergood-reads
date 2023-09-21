FROM node:19-bullseye-slim

# Set working directory
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Install node modules
COPY ./package.json /app
COPY ./package-lock.json /app
RUN npm install && npm cache clean --force

# Set ENV DJANGO_VITE_DEV_SERVER_PORT
ENV DJANGO_VITE_DEV_SERVER_PORT=""

# Copy application code to WORKDIR
COPY ./vite.config.js ${APP_HOME}
COPY ./supergood_reads ${APP_HOME}

ENTRYPOINT .demo/docker/images/node/scripts/entrypoint.sh
