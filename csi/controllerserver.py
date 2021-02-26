"""
controller server implementation
"""
import logging

import grpc

from . import csi_pb2
from . import csi_pb2_grpc
from .utils import log_request_and_reply

class ControllerServer(csi_pb2_grpc.ControllerServicer):
    """
    ControllerServer object is responsible for handling host
    volume mount and PV creation.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("ControllerServer")

    @log_request_and_reply
    def ControllerGetCapabilities(self, request, context):
        # using getattr to avoid Pylint error
        capability_type = getattr(
            csi_pb2.ControllerServiceCapability.RPC, "Type").Value

        return csi_pb2.ControllerGetCapabilitiesResponse(
            capabilities=[
                {
                    "rpc": {
                        "type": capability_type("CREATE_DELETE_VOLUME")
                    }
                },
            ]
        )

    @log_request_and_reply
    def ValidateVolumeCapabilities(self, request, context):
        # TODO
        pass

    @log_request_and_reply(fields=["name", "capacity_range", "volume_capabilities", "parameters"])
    def CreateVolume(self, request, context):
        caps = request.volume_capabilities[0] #TODO: iterate over volume_capabilities instead. could be multiple
        if caps.access_mode.mode not in [
                                csi_pb2.VolumeCapability.AccessMode.SINGLE_NODE_WRITER,
                                csi_pb2.VolumeCapability.AccessMode.SINGLE_NODE_READER_ONLY
                            ]:
            errmsg = f"Cannot handle {caps.access_mode}"
            self.logger.error(errmsg)
            context.set_details(errmsg)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return csi_pb2.CreateVolumeResponse()

        if not caps.HasField('mount'):
            errmsg = f"Invalid volume type. Can only handle 'mount'"
            self.logger.error(errmsg)
            context.set_details(errmsg)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return csi_pb2.CreateVolumeResponse()

        return csi_pb2.CreateVolumeResponse(
            volume={
                "volume_id": request.name,
                "capacity_bytes": request.capacity_range.required_bytes,
            }
        )

    @log_request_and_reply
    def DeleteVolume(self, request, context):
        return csi_pb2.DeleteVolumeResponse()
