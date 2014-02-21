server_names_hash_bucket_size 64;

upstream pushpenny {
	server 127.0.0.1:8000;
}

upstream blog {
	server 127.0.0.1:9000;
}

server {
        listen 80;
        server_name www.pushpenny.com;
        # $scheme will get the http protocol
        # and 301 is best practice for tablet, phone, desktop and seo
        return 301 $scheme://pushpenny.com$request_uri;
}

server {
        listen   80; 
	server_name pushpenny.com;
	
	location / {
		uwsgi_pass pushpenny;
		uwsgi_read_timeout 1800;
		include uwsgi_params;
		access_log /var/log/nginx/access.log;
	}

	location /robots.txt {
                alias   /var/apps/pushpenny.com/pushpenny/static/robots.txt;
        }

	# redirection to sitemap, hosted on Amazon S3
	rewrite ^/sitemap.xml http://s3.amazonaws.com/pushpenny/sitemap.xml permanent;

	# redirection to subscribe popup URL
	rewrite ^/subscribe$ /#subscribe permanent;
	rewrite ^/subscribe/$ /#subscribe permanent;

	# fallback URL redirection for pagination of category and merchant pages
	rewrite ^/categories/([a-zA-Z0-9-]+)/pages/([\d]+)/$ /categories/$1/page/$2/ permanent;
	rewrite ^/coupons/([a-zA-Z0-9-_]+)/([\d]+)/pages/([\d]+) /coupons/$1/$2/page/$3 permanent;

	location /static/ { 
        	# serve static media directly from nginx
		root /var/apps/pushpenny.com/pushpenny/;
		autoindex off;
		expires max;
		gzip on;
		gzip_buffers 16 8k;
		gzip_comp_level 4;
		gzip_http_version 1.0;
		gzip_min_length 1280;
		gzip_types text/css application/x-javascript text/javascript image/x-icon image/jpeg;
		gzip_vary on;
		gzip_disable "msi6";
    	}

	rewrite ^/blog/(.*)$ /magazine/$1 permanent;

	location /magazine/ {
		root /var/apps/pushpenny.com/;
		index index.php;
		try_files $uri $uri/ /magazine/index.php?$args;

		location ~* \.(html|htm|css|jpeg|jpg|gif|png)$ {
			# serve static files 
			log_not_found off;
		}

		location ~ \.php$ {
			fastcgi_pass blog;
			include fastcgi_params;
		}
	}
}

