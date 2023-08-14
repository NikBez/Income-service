from rest_framework import serializers


class PVZTotalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    total = serializers.FloatField()
    charged = serializers.FloatField()
    holded = serializers.FloatField()
    boxes = serializers.IntegerField()


class MonthResultsSerializer(serializers.Serializer):
    salaryes = serializers.FloatField()
    taxes = serializers.FloatField()
    profit = serializers.FloatField()


class WBMonitorSerializer(serializers.Serializer):
    pvz_total = PVZTotalSerializer(many=True)
    month_results = MonthResultsSerializer()
