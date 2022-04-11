FROM php:8.0-apache
RUN docker-php-ext-install mysqli
COPY config/ /var/www/config/

WORKDIR /var/www/html
COPY index.php index.php
COPY public/php/ php/
COPY public/js/ js/

EXPOSE 80
