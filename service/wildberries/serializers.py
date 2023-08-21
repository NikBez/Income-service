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
    total_outcome = serializers.DecimalField(max_digits=10, decimal_places=2)


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
    service = serializers.DecimalField(max_digits=10, decimal_places=2)
    income = serializers.DecimalField(max_digits=10, decimal_places=2)

class PVZOutcomesSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    date = serializers.DateField()
    sum = serializers.DecimalField(max_digits=10, decimal_places=2)
    category__title = serializers.CharField()
    description = serializers.CharField()

class TotalOutcomesSerializer(serializers.Serializer):
    category = serializers.CharField()
    outcome = serializers.DecimalField(max_digits=10, decimal_places=2)


class WBMonitorSerializer(serializers.Serializer):
    pvz_total = PVZTotalSerializer(many=True)
    month_results = MonthResultsSerializer()


class PVZMonitorSerializer(serializers.Serializer):
    pvz_total = PVZDetaledSerializer()
    employees = WeekEmployeeSerializer(many=True)
    pvz_outcomes = PVZOutcomesSerializer(many=True)
    total_outcomes = TotalOutcomesSerializer(many=True)
