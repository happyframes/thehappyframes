import traceback

from rest_framework import serializers


class Success:
    def __init__(self, data):
        self.data = data


class Failure:
    def __init__(self, data, code, msg, trace=None):
        self.data = data
        self.error_code = code
        self.error_msg = msg
        self.traceback = trace.split('\n') if trace else traceback.format_exc().split('\n')


class SuccessSerializer(serializers.Serializer):
    data = serializers.JSONField()


class FailureSerializer(serializers.Serializer):
    data = serializers.ReadOnlyField()
    error_code = serializers.IntegerField()
    error_msg = serializers.CharField()
    traceback = serializers.CharField()
