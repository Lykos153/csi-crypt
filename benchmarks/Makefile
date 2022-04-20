fio_plot_version = "1.0.8"

.PHONY: all
all: deploy

.PHONY: image  # Build the image
image:
	docker build -t $(image_name) --build-arg FIO_PLOT_VERSION=$(fio_plot_version) .

.PHONY: push # Push the image to the registry
push: image
	docker push $(image_name)

.PHONY: cleandeploy # Delte old deployments and run benchmark in the cluster
cleandeploy: clean-remote deploy

.PHONY: deploy # Run the benchmark in the cluster
.EXPORT_ALL_VARIABLES:
export BENCHMARK_IMAGE=$(image_name)
deploy: push
	envsubst < benchmark-deployment.yaml | \
		kubectl apply -n $(namespace) -f -
	

.PHONY: clean  # Delete local images and remote deployment
clean: clean-local clean-remote

.PHONY: clean-local  # Delete local files and images
clean-local:
	docker image rm -f $(image_name)

.PHONY: clean-remote  # Delete remote deployment
clean-remote:
	-envsubst < benchmark-deployment.yaml | \
		kubectl delete --grace-period 0 --force -n $(namespace) -f -

.PHONY: help # Generate list of targets with descriptions                                                                
help:                                                                                                                    
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1###\2/' |  column -t  -s '###'
