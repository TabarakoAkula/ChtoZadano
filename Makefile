update:
	git pull
	docker compose restart

sort-req:
	sort-requirements requirements/prod.txt
	sort-requirements requirements/dev.txt
	sort-requirements requirements/test.txt

docker-clean-all:
	docker compose stop
	docker system prune

docker-clean-old:
	docker system prune -a

docker-rebuildup:
	docker compose stop
	docker compose up --build -d

docker-bash-web:
	docker exec -it chtozadano-web-1 bash

docker-psql:
	docker exec -it db psql -U postgres
