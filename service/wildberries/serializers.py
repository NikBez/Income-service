from rest_framework import serializers


class PVZTotalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    total = serializers.FloatField()
    charged = serializers.FloatField()
    holded = serializers.FloatField()
    boxes = serializers.IntegerField()


class WBMonitorSerializer(serializers.Serializer):
    pvz_total = PVZTotalSerializer(many=True)
