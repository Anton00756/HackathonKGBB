shared = true


up: down delete_trash
    ifeq ($(shared), true)
		@docker-compose --env-file .env -f=docker_files/docker-compose-shared.yaml -p kgbb up -d
    else
		@docker-compose --env-file .env -f=docker_files/docker-compose.yaml -p kgbb up -d
    endif

down:
	@docker-compose -p kgbb down

delete_trash:
	@docker volume rm -f $(shell docker volume ls -q | grep -v "grafana" | grep -v "influx") || true
	@docker system prune -f

clear_metrics:
	@docker exec -it influx influx delete --org KGBB --bucket metrics --start 2000-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z