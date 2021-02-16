"""
nodeserver implementation
"""
import logging

import csi_pb2
import csi_pb2_grpc



class NodeServer(csi_pb2_grpc.NodeServicer):
    """
    NodeServer object is responsible for handling host
    volume mount and PV mounts.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """
    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("NodeServer")

    def NodeGetCapabilities(self, request, context):
        self.logger.debug("Received request: NodeGetCapabilities")
        return csi_pb2.NodeGetCapabilitiesResponse()

    def NodePublishVolume(self, request, context):
        self.logger.debug("Received request: NodePublishVolume for {}".format(volume=request.volume_id))
        return csi_pb2.NodePublishVolumeResponse()

    def NodeUnpublishVolume(self, request, context):
        self.logger.debug("Received request: NodeUnpublishVolume for {}".format(volume=request.volume_id))
        return csi_pb2.NodeUnpublishVolumeResponse()
