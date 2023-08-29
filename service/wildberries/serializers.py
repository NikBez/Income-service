from rest_framework import serializers


class PVZTotalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    charged = serializers.DecimalField(max_digits=10, decimal_places=2)
    holded = serializers.DecimalField(max_digits=10, decimal_places=2)
    boxes = serializers.IntegerField()


class PVZDetaledSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    rent_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    charged = serializers.DecimalField(max_digits=10, decimal_places=2)
    holded = serializers.DecimalField(max_digits=10, decimal_places=2)
    boxes = serializers.IntegerField()
    add_penalty = serializers.DecimalField(max_digits=10, decimal_places=2)
    sub_penalty = serializers.DecimalField(max_digits=10, decimal_places=2)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2)
    taxes = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_outcome = serializers.DecimalField(max_digits=10, decimal_places=2)


class WeekEmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    penalty = serializers.DecimalField(max_digits=10, decimal_places=2)
    days = serializers.IntegerField()
    extra = serializers.DecimalField(max_digits=10, decimal_places=2)
    add_penalty = serializers.DecimalField(max_digits=10, decimal_places=2)
    surcharge_penalty = serializers.DecimalField(max_digits=10, decimal_places=2)
    payed = serializers.DecimalField(max_digits=10, decimal_places=2)
    boxes = serializers.IntegerField()
    to_pay = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class MonthResultsSerializer(serializers.Serializer):
    salaryes = serializers.DecimalField(max_digits=10, decimal_places=2)
    taxes = serializers.DecimalField(max_digits=10, decimal_places=2)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2)
    rent = serializers.DecimalField(max_digits=10, decimal_places=2)
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


class MonthNamesSerializer(serializers.Serializer):
    names = serializers.ListSerializer


class WBMonitorSerializer(serializers.Serializer):
    pvz_total = PVZTotalSerializer(many=True)
    month_results = MonthResultsSerializer()
    month_names = serializers.ListSerializer(child=serializers.CharField())
    profits = serializers.ListSerializer(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    income = serializers.ListSerializer(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    salary = serializers.ListSerializer(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    rent = serializers.ListSerializer(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    service = serializers.ListSerializer(child=serializers.DecimalField(max_digits=10, decimal_places=2))


class PVZMonitorSerializer(serializers.Serializer):
    pvz_total = PVZDetaledSerializer()
    employees = WeekEmployeeSerializer(many=True)
    pvz_outcomes = PVZOutcomesSerializer(many=True)
    total_outcomes = TotalOutcomesSerializer(many=True)
