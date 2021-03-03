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
from . import kube



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
        self.kube_client = kube.NodeApiClient(kubelet_dir, node_name)

    @log_request_and_reply
    def NodeGetCapabilities(self, request, context):
        return csi_pb2.NodeGetCapabilitiesResponse()

    @log_request_and_reply(fields=["volume_id", "target_path"])
    def NodePublishVolume(self, request, context):
        encrypter_name = self._encrypter_name_from_volume_id(request.volume_id)
        self.logger.debug(f"Spawning Encrypter {encrypter_name}")
        self.kube_client.create_encrypter(
            name=encrypter_name,
            volume_id=request.volume_id,
            backendClaimName=request.volume_context['backend_claim_name'],
        )

        return csi_pb2.NodePublishVolumeResponse()


    @log_request_and_reply(fields=["volume_id"])
    def NodeUnpublishVolume(self, request, context):
        encrypter_name = self._encrypter_name_from_volume_id(request.volume_id)
        self.logger.debug(f"Deleting Encrypter {encrypter_name}")
        self.kube_client.delete_encrypter(encrypter_name)

        return csi_pb2.NodeUnpublishVolumeResponse()

    @log_request_and_reply
    def NodeGetInfo(self, request, context):
        return csi_pb2.NodeGetInfoResponse(node_id=self.node_name[0:128])

    def _encrypter_name_from_volume_id(self, volume_id: str):
        return f"encrypter-{volume_id}"
