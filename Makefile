package_dir = csi
gocryptfs_encrypter_image_name = $(image_name):gocryptfs
gocryptfs_encrypter_dir = gocryptfs
dummy_encrypter_image_name = $(image_name):dummy
dummy_encrypter_dir = encrypter-dummy
benchmark_image_name = $(image_name):benchmark
namespace = lcrypt
pull_secret = regcred-cah-csi
application_name = lcrypt
backend_storage_class = local-path

.PHONY: build # Same as 'image'
build: image

.PHONY: app-local # Build the app for local testing
app-local:  
	make -C $(package_dir)

.PHONY: csi image  # Build the image
csi image:
	docker build -t $(image_name) --build-arg package_dir=$(package_dir) .

.PHONY: gocryptfs # Build the gocryptfs encrypter image
gocryptfs:
	image_name="$(gocryptfs_encrypter_image_name)" make -C $(gocryptfs_encrypter_dir)

.PHONY: dummy-encrypter # Build the gocryptfs encrypter image
dummy-encrypter:
	image_name="$(dummy_encrypter_image_name)" make -C $(dummy_encrypter_dir)

.PHONY: benchmark # Run the fio benchmark in the cluster
benchmark:
	image_name=$(benchmark_image_name) \
	namespace=$(namespace) \
	PULL_SECRET_NAME=$(pull_secret) \
	STORAGE_CLASS_ENCRYPTED=lcrypt \
	STORAGE_CLASS_UNENCRYPTED=$(backend_storage_class) \
	CLAIMSIZE=1G \
	TESTFILE_SIZE=10M \
	BLOCKSIZE="4k" \
	NUMJOBS="8" \
	IODEPTH="8" \
	LOOPS=10 \
	MODE="write randwrite" \
	RWMIXREAD="75" \
	make -C benchmarks cleandeploy

.encrypter_digest: gocryptfs
	docker image list --digests | awk "{if (\$$1 == \"$(image_name)\" && \$$2 == \"gocryptfs\") {print \$$3;}}" > $@

.PHONY: push # Push the image to the registry
push: image gocryptfs dummy-encrypter
	docker push $(image_name)
	docker push $(gocryptfs_encrypter_image_name)
	docker push $(dummy_encrypter_image_name)

.PHONY: deploy # Deploy the kubernetes resources
deploy: .encrypter_digest #while debugging 
	helm upgrade --install $(application_name) helm/lcrypt \
		--namespace=$(namespace) \
		--create-namespace \
		--set imageName=$(image_name) \
		--set namespace=$(namespace) \
		--set pullSecret=$(pull_secret) \
		--set provisioner.backendStorageClass=$(backend_storage_class) \
		--set nodeplugin.encrypterImageName=$(image_name)@$(shell cat .encrypter_digest) \
		--set nodeplugin.encrypterPullSecret=$(pull_secret)

.PHONY: rollout # Rollout the application to the cluster
rollout: push deploy
	kubectl -n $(namespace) rollout restart daemonset lcrypt-csi-nodeplugin
	kubectl -n $(namespace) rollout restart deployment lcrypt-csi-provisioner

.PHONY: clean  # Delete local files and images
clean:
	make clean -C $(package_dir)
	make clean -C benchmarks
	make clean -C $(gocryptfs_encrypter_dir)
	make clean -C $(dummy_encrypter_dir)
	docker image rm -f $(image_name)
	rm -f .encrypter_digest

.PHONY: help # Generate list of targets with descriptions
help:                                                                                                                    
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1###\2/' |  column -t  -s '###'
