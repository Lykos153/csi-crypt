.PHONY: build-grpc clean

build-grpc: csi/protos/csi.proto
	python3 -m grpc_tools.protoc -I./csi/protos --python_out=csi --grpc_python_out=csi ./csi/protos/csi.proto

csi/protos/csi.proto:
	mkdir -p csi/protos
	curl -o csi/protos/csi.proto "https://raw.githubusercontent.com/container-storage-interface/spec/v1.3.0/csi.proto"

clean:
	rm csi/protos/csi.proto
