FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html 404.html robots.txt /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js
COPY en /usr/share/nginx/html/en
COPY fr /usr/share/nginx/html/fr
COPY es /usr/share/nginx/html/es
COPY ar /usr/share/nginx/html/ar
COPY zh /usr/share/nginx/html/zh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/healthz || exit 1
