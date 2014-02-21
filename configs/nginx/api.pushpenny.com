upstream pushpenny_mobile {
        server 127.0.0.1:8100;
}

server {
	listen 80;

	server_name api.pushpenny.com;
	access_log /var/log/nginx/api.access.log;

	# fallback rewrite from old API URLs to new ones
	rewrite ^/v2/deals(.*)$ /v3/deals$1 break;
	rewrite ^/v2/localinfo(.*)$ /v3/localinfo$1 break;

	location / {
                uwsgi_pass pushpenny_mobile;
                include uwsgi_params;
	}

}

