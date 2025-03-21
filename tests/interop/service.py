#!/usr/bin/env python3
# pyvider/ctytest/service.py

from typing import Any


from pyvider.rpcplugin.protocol import RPCPluginProtocol
from pyvider.cty.logger import logger

from .proto import ctytest_pb2, ctytest_pb2_grpc

class CtyTestService(ctytest_pb2_grpc.CtyTestServicer):
    """Implementation of the CtyTest service using pyvider.cty."""
    
    async def CreateType(self, request, context):
        """Create a CtyType from the specification."""
        logger.debug(f"🧰🚀✅ Creating type: {request.type_kind}")
        try:
            # Convert from protobuf request to TypeSpec
            type_spec = TypeSpec(
                type_kind=request.type_kind,
                params=json.loads(request.params_json)
            )
            
            # Create the actual type
            cty_type = type_spec.to_cty_type()
            
            # Convert result back to protobuf
            return ctytest_pb2.TypeResponse(
                success=True,
                type_spec=type_spec.to_proto()
            )
        except Exception as e:
            logger.error(f"🧰❌❌ Error creating type: {e}")
            return ctytest_pb2.TypeResponse(
                success=False,
                error_message=str(e)
            )
    
    async def PerformOperation(self, request, context):
        """Perform an operation on Cty values."""
        logger.debug(f"🧰🚀✅ Performing operation: {request.operation}")
        try:
            # Convert input values from protobuf
            left_value = ValueSpec.from_proto(request.left_value).to_cty_value()
            
            # Handle unary vs binary operations
            result = None
            match request.operation:
                case "add": 
                    right_value = ValueSpec.from_proto(request.right_value).to_cty_value()
                    result = left_value + right_value
                case "negate":
                    result = -left_value
                # ... other operations ...
            
            # Convert result back to protobuf
            return ctytest_pb2.ValueResponse(
                success=True,
                value=ValueSpec.from_cty_value(result).to_proto()
            )
        except Exception as e:
            logger.error(f"🧰❌❌ Operation failed: {e}")
            return ctytest_pb2.ValueResponse(
                success=False,
                error_message=str(e)
            )
    
    # ... implement other methods ...

class CtyTestProtocol(RPCPluginProtocol):
    """Protocol definition for the Cty test service."""
    
    def get_grpc_descriptors(self) -> tuple[Any, str]:
        """Returns the gRPC descriptors for this protocol."""
        return ctytest_pb2.DESCRIPTOR, "ctytest.CtyTest"
    
    async def add_to_server(self, handler, server) -> None:
        """Add the Cty test service to the gRPC server."""
        ctytest_pb2_grpc.add_CtyTestServicer_to_server(CtyTestService(), server)
