FROM node:19-bullseye-slim

# Set working directory
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Install node modules
COPY ./package.json /app
COPY ./package-lock.json /app
RUN npm install && npm cache clean --force

# Copy application code to WORKDIR
COPY ./vite.config.js .
COPY ./tailwind.config.js .
COPY ./tsconfig.json .
COPY ./supergood_reads .
COPY ./deploy/docker/images/vite/scripts ./deploy/docker/images/vite/scripts

ENTRYPOINT ./deploy/docker/images/vite/scripts/entrypoint.sh
