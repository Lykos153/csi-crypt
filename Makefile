.PHONY: build-grpc clean build-image push-image deploy-helm

proto_dir = csi/protos
package_dir = csi
namespace = kube-system
pull_secret = regcred-cah-csi
application_name = lcrypt

build-grpc: $(proto_dir)/csi.proto
	python3 -m grpc_tools.protoc -I./$(proto_dir) --python_out=$(package_dir) --grpc_python_out=$(package_dir) $<

$(proto_dir)/csi.proto:
	mkdir -p $(proto_dir)
	curl -o $@ "https://raw.githubusercontent.com/container-storage-interface/spec/v1.3.0/csi.proto"

build-image:
	docker build -t $(image_name) .

push-image: build-image
	docker push $(image_name)

deploy-helm: push-image
	helm upgrade --install $(application_name) helm/lcrypt \
		--set imageName=$(image_name) \
		--set namespace=$(namespace) \
		--set pullSecret=$(pull_secret)

rollout: push-image deploy-helm
	kubectl -n $(namespace) rollout restart daemonset lcrypt-csi-nodeplugin
	kubectl -n $(namespace) rollout restart statefulset lcrypt-csi-provisioner

clean:
	rm $(proto_dir)/csi.proto
	rm $(package_dir)/csi_pb2.py $(package_dir)/csi_pb2_grpc.py
	docker image rm $(image_name)
