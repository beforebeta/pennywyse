<VirtualHost *:80>
        ServerName pennywyse.com
        ServerAlias www.pennywyse.com
        WSGIScriptAlias / /root/public_html/pennywyse/launch.wsgi
        Alias /static/ /root/public_html/pennywyse/static/
        <Location "/static/">
            Options -Indexes
        </Location>
        AllowEncodedSlashes On
</VirtualHost>