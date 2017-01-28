FROM debian
MAINTAINER Menshikh Ivan <menshikh.iv@gmail.com>

RUN apt-get update && \
    apt-get install -y nginx supervisor python-dev python-pip uwsgi-plugin-python uwsgi-plugin-python libzmq-dev

RUN pip install --upgrade pip
RUN pip install uwsgi flask numpy scipy zmq plotly markdown


COPY app /var/www/app
COPY site-dev.conf /etc/nginx/sites-available/site.conf
COPY supervisord.conf /etc/supervisor/conf.d/

RUN mkdir -p /var/log/nginx/app /var/log/uwsgi/app /var/log/supervisor && \
    rm /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/site.conf && \
    echo "daemon off;" >> /etc/nginx/nginx.conf && \
    chown -R www-data:www-data /var/www/app && \
    chown -R www-data:www-data /var/log

CMD ["/usr/bin/supervisord"]
