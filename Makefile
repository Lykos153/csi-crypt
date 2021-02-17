.PHONY: build-grpc clean

proto_dir = csi/protos
package_dir = csi

build-grpc: $(proto_dir)/csi.proto
	python3 -m grpc_tools.protoc -I./$(proto_dir) --python_out=$(package_dir) --grpc_python_out=$(package_dir) $<

$(proto_dir)/csi.proto:
	mkdir -p $(proto_dir)
	curl -o $@ "https://raw.githubusercontent.com/container-storage-interface/spec/v1.3.0/csi.proto"

clean:
	rm $(proto_dir)/csi.proto
	rm $(package_dir)/csi_pb2.py $(package_dir)/csi_pb2_grpc.py
