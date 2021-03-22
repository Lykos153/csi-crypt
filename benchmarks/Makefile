fio_plot_version = "1.0.8"

.PHONY: all
all: deploy

.PHONY: image  # Build the image
image:
	docker build -t $(image_name) --build-arg FIO_PLOT_VERSION=$(fio_plot_version) .

.PHONY: push # Push the image to the registry
push: image
	docker push $(image_name)

.PHONY: deploy # Run the benchmark in the cluster
.EXPORT_ALL_VARIABLES:
export BENCHMARK_IMAGE=$(image_name)
deploy: push
	envsubst < benchmark-deployment.yaml | \
		kubectl apply -n $(namespace) -f -
	

.PHONY: clean  # Delete local files and images
clean:
	docker image rm -f $(image_name)
	envsubst < benchmark-deployment.yaml | \
		kubectl delete -n $(namespace) -f -

.PHONY: help # Generate list of targets with descriptions                                                                
help:                                                                                                                    
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1###\2/' |  column -t  -s '###'
