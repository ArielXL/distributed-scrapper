.PHONY: clean

NAME 	   	:= Distributed Scrapper
VERSION		:= 2.0
DEVELOPERS	:= Reinaldo Barrera Travieso, Ariel Plasencia Díaz
COPYRIGHT  	:= Copyright © 2021: $(DEVELOPERS)
EXECUTE 	:= $($(target))

info: ## Display project description
	@echo "$(NAME) v$(VERSION)"
	@echo "$(COPYRIGHT)"

version: ## Show the project version
	@echo "$(NAME) v$(VERSION)"

server: ## Run a server with default parameters
	$(EXECUTE) python server.py --ip 127.0.0.1 --port 8080 --level 1

client: ## Run a client with default parameters
	$(EXECUTE) python client.py --ip 127.0.0.1 --port 9090 --level 1

install: ## Install the project dependencies
	pip install beautifulsoup4

clean: ## Remove temporary files
	rm -rf downloads/*
	rm -rf __pycache__/
	rm -rf chord/__pycache__/
	rm -rf utils/__pycache__/
	rm -rf scrapper/__pycache__/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

