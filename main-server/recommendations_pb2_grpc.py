# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import recommendations_pb2 as recommendations__pb2


class RecommendationManagerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.choose_task_for_user = channel.unary_unary(
                '/RecommendationManager/choose_task_for_user',
                request_serializer=recommendations__pb2.TaskRequest.SerializeToString,
                response_deserializer=recommendations__pb2.TaskResponse.FromString,
                )


class RecommendationManagerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def choose_task_for_user(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RecommendationManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'choose_task_for_user': grpc.unary_unary_rpc_method_handler(
                    servicer.choose_task_for_user,
                    request_deserializer=recommendations__pb2.TaskRequest.FromString,
                    response_serializer=recommendations__pb2.TaskResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RecommendationManager', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RecommendationManager(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def choose_task_for_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RecommendationManager/choose_task_for_user',
            recommendations__pb2.TaskRequest.SerializeToString,
            recommendations__pb2.TaskResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
