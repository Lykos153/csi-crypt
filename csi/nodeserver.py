"""
nodeserver implementation
"""
import os
import logging

from . import csi_pb2
from . import csi_pb2_grpc
from .utils import log_request_and_reply



class NodeServer(csi_pb2_grpc.NodeServicer):
    """
    NodeServer object is responsible for handling host
    volume mount and PV mounts.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("NodeServer")

    @log_request_and_reply
    def NodeGetCapabilities(self, request, context):
        return csi_pb2.NodeGetCapabilitiesResponse()

    @log_request_and_reply(fields=["volume_id"])
    def NodePublishVolume(self, request, context):
        return csi_pb2.NodePublishVolumeResponse()

    @log_request_and_reply(fields=["volume_id"])
    def NodeUnpublishVolume(self, request, context):
        return csi_pb2.NodeUnpublishVolumeResponse()

    @log_request_and_reply
    def NodeGetInfo(self, request, context):
        return csi_pb2.NodeGetInfoResponse(
            node_id=os.environ["NODE_ID"][0:128], #128 byte is RECOMMENDED for best backwards compatibility
        )
