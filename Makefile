.PHONY: app-local clean image push deploy

package_dir = csi
namespace = kube-system
pull_secret = regcred-cah-csi
application_name = lcrypt

build: image

app-local:  
	make -C $(package_dir)

image:
	docker build -t $(image_name) --build-arg package_dir=$(package_dir) .

push: image
	docker push $(image_name)

deploy: push
	helm upgrade --install $(application_name) helm/lcrypt \
		--set imageName=$(image_name) \
		--set namespace=$(namespace) \
		--set pullSecret=$(pull_secret)

rollout: push deploy
	kubectl -n $(namespace) rollout restart daemonset lcrypt-csi-nodeplugin
	kubectl -n $(namespace) rollout restart statefulset lcrypt-csi-provisioner

clean:
	make clean -C $(package_dir)
	docker image rm -f $(image_name)
