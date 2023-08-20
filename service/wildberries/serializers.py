from rest_framework import serializers


class PVZTotalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    total = serializers.FloatField()
    charged = serializers.FloatField()
    holded = serializers.FloatField()
    boxes = serializers.IntegerField()


class PVZDetaledSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    rent_price = serializers.FloatField()
    income = serializers.FloatField()
    charged = serializers.FloatField()
    holded = serializers.FloatField()
    boxes = serializers.IntegerField()
    add_penalty = serializers.FloatField()
    sub_penalty = serializers.FloatField()
    salary = serializers.FloatField()
    profit = serializers.FloatField()
    taxes = serializers.FloatField()


class WeekEmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    salary = serializers.FloatField()
    penalty = serializers.FloatField()
    days = serializers.IntegerField()
    extra = serializers.FloatField()
    add_penalty = serializers.FloatField()
    surcharge_penalty = serializers.FloatField()
    total = serializers.FloatField()
    boxes = serializers.IntegerField()


class MonthResultsSerializer(serializers.Serializer):
    salaryes = serializers.FloatField()
    taxes = serializers.FloatField()
    profit = serializers.FloatField()
    rent = serializers.FloatField()


class WBMonitorSerializer(serializers.Serializer):
    pvz_total = PVZTotalSerializer(many=True)
    month_results = MonthResultsSerializer()


class PVZMonitorSerializer(serializers.Serializer):
    pvz_total = PVZDetaledSerializer()
    employees = WeekEmployeeSerializer(many=True)
