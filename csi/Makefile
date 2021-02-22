.PHONY: all clean

proto_dir = protos

all: csi_pb2.py csi_pb2_grpc.py

csi_pb2.py csi_pb2_grpc.py &: $(proto_dir)/csi.proto
	python3 -m grpc_tools.protoc -I./$(proto_dir) --python_out=. --grpc_python_out=. $<
	# Fix generated relative import https://github.com/grpc/grpc/issues/2010#issuecomment-110495155
	sed -i -E 's/^import.*_pb2/from . \0/' csi_pb2_grpc.py

$(proto_dir)/csi.proto:
	mkdir -p $(proto_dir)
	curl -o $@ "https://raw.githubusercontent.com/container-storage-interface/spec/v1.3.0/csi.proto"

clean:
	rm -f $(proto_dir)/csi.proto
	rm -f csi_pb2.py csi_pb2_grpc.py
