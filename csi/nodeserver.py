"""
nodeserver implementation
"""
import logging
import subprocess
from pathlib import Path

import grpc

from . import csi_pb2
from . import csi_pb2_grpc
from .utils import log_request_and_reply



class NodeServer(csi_pb2_grpc.NodeServicer):
    """
    NodeServer object is responsible for handling host
    volume mount and PV mounts.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """
    def __init__(self, node_name: str, kubelet_dir: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("NodeServer")
        self.node_name = node_name
        self.kubelet_dir = kubelet_dir

    @log_request_and_reply
    def NodeGetCapabilities(self, request, context):
        return csi_pb2.NodeGetCapabilitiesResponse()

    @log_request_and_reply(fields=["volume_id", "target_path"])
    def NodePublishVolume(self, request, context):
        source_path = Path("/tmp/", request.volume_id)
        target_path = Path(request.target_path)
        source_path.mkdir(parents=True, exist_ok=True)
        target_path.mkdir()

        test_file = source_path / "test"
        test_file.touch()

        try:
            subprocess.check_output(["mount", "--bind", source_path, str(target_path)])

        except subprocess.CalledProcessError as e:
            errmsg = f"Failed to mount {target_path}. Command returned with {e.returncode}" \
                     f"Captured output: {e.output}"
            self.logger.error(errmsg)
            context.set_details(errmsg)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return csi_pb2.CreateVolumeResponse()

        return csi_pb2.NodePublishVolumeResponse()

    @log_request_and_reply(fields=["volume_id"])
    def NodeUnpublishVolume(self, request, context):
        target_path = Path(request.target_path)
        try:
            subprocess.check_output(["umount", str(target_path)])
        except subprocess.CalledProcessError as e:
            errmsg = f"Failed to unmount {target_path}. Command returned with {e.returncode}" \
                     f"Captured output: {e.output}"
            self.logger.error(errmsg)
            context.set_details(errmsg)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        target_path.rmdir()
        return csi_pb2.NodeUnpublishVolumeResponse()

    @log_request_and_reply
    def NodeGetInfo(self, request, context):
        return csi_pb2.NodeGetInfoResponse(node_id=self.node_name[0:128])
