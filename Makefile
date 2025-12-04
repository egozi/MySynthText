.PHONY: help build build-nocache run run-shell run-jupyter clean docker-clean logs ps inspect example-run example-shell

# Configuration
IMAGE_NAME := synthtext
IMAGE_TAG := latest
DATA_PATH ?= $(PWD)/data
RESULTS_PATH ?= $(PWD)/results
CONTAINER_WORKDIR := /opt/app/MySynthText

help:
	@echo "MySynthText Docker Makefile"
	@echo "============================"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make build              Build the Docker image (no cache)"
	@echo "  make build-nocache      Build the Docker image without using cache"
	@echo "  make run                Run the container with gen.py"
	@echo "  make run-shell          Run the container with interactive shell"
	@echo "  make run-jupyter        Run the container with Jupyter notebook"
	@echo "  make clean              Stop and remove running container"
	@echo "  make docker-clean       Remove Docker image"
	@echo ""
	@echo "Configuration (use with environment variables):"
	@echo "  DATA_PATH               Path to data folder (default: $(DATA_PATH))"
	@echo "  RESULTS_PATH            Path to results folder (default: $(RESULTS_PATH))"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make run DATA_PATH=/custom/data RESULTS_PATH=/custom/results"
	@echo "  make run-shell"
	@echo "  make run-jupyter"

build:
	@echo "Building Docker image: $(IMAGE_NAME):$(IMAGE_TAG) (without cache)"
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Build complete!"

build-nocache:
	@echo "Building Docker image: $(IMAGE_NAME):$(IMAGE_TAG) (without cache)"
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Build complete!"

run:
	@echo "Running gen.py with:"
	@echo "  Data folder: $(DATA_PATH)"
	@echo "  Results folder: $(RESULTS_PATH)"
	@echo ""
	@echo "Enabling X11 forwarding for plotting..."
	@xhost +local:docker > /dev/null 2>&1 || true
	@echo ""
	docker run --rm \
		-e DISPLAY=$(DISPLAY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v "$(DATA_PATH):$(CONTAINER_WORKDIR)/data" \
		-v "$(RESULTS_PATH):$(CONTAINER_WORKDIR)/results" \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		python gen.py

run-shell:
	@echo "Running interactive shell with:"
	@echo "  Data folder: $(DATA_PATH)"
	@echo "  Results folder: $(RESULTS_PATH)"
	@echo ""
	@echo "Enabling X11 forwarding for plotting..."
	@xhost +local:docker > /dev/null 2>&1 || true
	@echo ""
	docker run -it --rm \
		-e DISPLAY=$(DISPLAY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v "$(DATA_PATH):$(CONTAINER_WORKDIR)/data" \
		-v "$(RESULTS_PATH):$(CONTAINER_WORKDIR)/results" \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		bash

run-jupyter:
	@echo "Running Jupyter notebook with:"
	@echo "  Data folder: $(DATA_PATH)"
	@echo "  Results folder: $(RESULTS_PATH)"
	@echo ""
	@echo "Jupyter will be available at http://localhost:8888"
	@echo ""
	@echo "Enabling X11 forwarding for plotting..."
	@xhost +local:docker > /dev/null 2>&1 || true
	@echo ""
	docker run -it --rm \
		-p 8888:8888 \
		-e DISPLAY=$(DISPLAY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v "$(DATA_PATH):$(CONTAINER_WORKDIR)/data" \
		-v "$(RESULTS_PATH):$(CONTAINER_WORKDIR)/results" \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		bash -c "pip install jupyter && jupyter notebook --ip=0.0.0.0 --no-browser --allow-root"

clean:
	@echo "Stopping and removing containers..."
	docker ps -a | grep $(IMAGE_NAME) | awk '{print $$1}' | xargs -r docker rm -f
	@echo "Clean complete!"

docker-clean: clean
	@echo "Removing Docker image: $(IMAGE_NAME):$(IMAGE_TAG)"
	docker rmi -f $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Docker clean complete!"

# Development helpers
logs:
	docker logs -f $$(docker ps -q --filter "ancestor=$(IMAGE_NAME):$(IMAGE_TAG)")

ps:
	@echo "Running containers:"
	docker ps --filter "ancestor=$(IMAGE_NAME):$(IMAGE_TAG)"

inspect:
	@echo "Image details for $(IMAGE_NAME):$(IMAGE_TAG)"
	docker inspect $(IMAGE_NAME):$(IMAGE_TAG)

# Advanced usage examples
example-run:
	@echo "Example: Running with custom data folder"
	@echo "make run DATA_PATH=/home/user/my_data RESULTS_PATH=/home/user/my_results"

example-shell:
	@echo "Example: Running shell with custom paths"
	@echo "make run-shell DATA_PATH=/home/user/my_data RESULTS_PATH=/home/user/my_results"
