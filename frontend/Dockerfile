# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:14.15
# Puppeteer dependencies, from: https://github.com/GoogleChrome/puppeteer/blob/master/docs/troubleshooting.md#running-puppeteer-in-docker
# Install latest chrome dev package and fonts to support major charsets (Chinese, Japanese, Arabic, Hebrew, Thai and a few others)
# Note: this installs the necessary libs to make the bundled version of Chromium that Puppeteer
# installs, work.
ARG INSTALL_PUPPETEER=false
RUN bash -c "if [ $INSTALL_PUPPETEER == 'true' ] ; then apt-get update && apt-get install -y wget --no-install-recommends \
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google.list' \
  && apt-get update \
  && apt-get install -y google-chrome-unstable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst ttf-freefont \
  --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get purge --auto-remove -y curl \
  && rm -rf /src/*.deb; fi"
WORKDIR /app
RUN bash -c "if [ $INSTALL_PUPPETEER == 'true' ] ; then npm install puppeteer ; fi"
COPY package*.json /app/
RUN npm install
COPY ./ /app/
ARG FRONTEND_ENV=production
ENV ANGULAR_APP_ENV=${FRONTEND_ENV}
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then npm install -g @angular/cli ; fi"
EXPOSE 4200
CMD npm run start
