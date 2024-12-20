shared = true


up: down delete_trash
    ifeq ($(shared), true)
		@docker-compose -f=docker_files/docker-compose-shared.yaml -p kgbb up -d
    else
		@docker-compose -f=docker_files/docker-compose.yaml -p kgbb up -d
    endif

down:
	@docker-compose -p kgbb down

delete_trash:
	@docker volume rm -f $(shell docker volume ls -q | grep -v "grafana" | grep -v "influx") || true
	@docker system prune -f