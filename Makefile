package_dir = csi
namespace = lcrypt
pull_secret = regcred-cah-csi
application_name = lcrypt
backend_storage_class = ""

.PHONY: build # Same as 'image'
build: image

.PHONY: app-local # Build the app for local testing
app-local:  
	make -C $(package_dir)

.PHONY: image  # Build the image
image:
	docker build -t $(image_name) --build-arg package_dir=$(package_dir) .

.PHONY: push # Push the image to the registry
push: image
	docker push $(image_name)

.PHONY: deploy # Deploy the kubernetes resources
deploy:
	helm upgrade --install $(application_name) helm/lcrypt \
		--namespace=$(namespace) \
		--create-namespace \
		--set imageName=$(image_name) \
		--set namespace=$(namespace) \
		--set pullSecret=$(pull_secret) \
		--set provisioner.backendStorageClass=$(backend_storage_class)

.PHONY: rollout # Rollout the application to the cluster
rollout: push deploy
	kubectl -n $(namespace) rollout restart daemonset lcrypt-csi-nodeplugin
	kubectl -n $(namespace) rollout restart statefulset lcrypt-csi-provisioner

.PHONY: clean  # Delete local files and images
clean:
	make clean -C $(package_dir)
	docker image rm -f $(image_name)

.PHONY: help # Generate list of targets with descriptions                                                                
help:                                                                                                                    
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1###\2/' |  column -t  -s '###'
