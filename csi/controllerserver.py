"""
controller server implementation
"""
import logging

import grpc

from . import csi_pb2
from . import csi_pb2_grpc
from .utils import log_request_and_reply
from . import kube

class ControllerServer(csi_pb2_grpc.ControllerServicer):
    """
    ControllerServer object is responsible for handling host
    volume mount and PV creation.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """

    def __init__(self, backend_storage_class: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("ControllerServer")
        self.kube_client = kube.ControllerApiClient()
        self.backend_storage_class = backend_storage_class

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

        backend_claim_name = f"backend-{request.name}"
        self.logger.debug(f"Creating Backend PVC {backend_claim_name}")
        self.kube_client.create_pvc(
            name=backend_claim_name,
            capacity_bytes=request.capacity_range.required_bytes,
            #TODO: Can we use the actual capacity ranges here?
            backend_class=self.backend_storage_class,
        )

        return csi_pb2.CreateVolumeResponse(
            volume={
                "volume_id": request.name,
                "capacity_bytes": request.capacity_range.required_bytes,
                "volume_context": {
                    "backend_claim_name": backend_claim_name,
                }
            },
        )

    @log_request_and_reply
    def DeleteVolume(self, request, context):
        return csi_pb2.DeleteVolumeResponse()
