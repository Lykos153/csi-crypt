gocryptfs_version = "1.8.0"

.PHONY: image  # Build the image
image:
	docker build -t $(image_name) --build-arg GOCRYPTFS_VERSION=$(gocryptfs_version) .

.PHONY: push # Push the image to the registry
push: image
	docker push $(image_name)


.PHONY: clean  # Delete local files and images
clean:
	docker image rm -f $(image_name)

.PHONY: help # Generate list of targets with descriptions                                                                
help:                                                                                                                    
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1###\2/' |  column -t  -s '###'
