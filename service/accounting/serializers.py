from rest_framework import serializers

from .models import Income


class IncomesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'


class SumBySourceSerializer(serializers.Serializer):
    source__title = serializers.CharField()
    sum_of_income = serializers.FloatField()


class SumByCategorySerializer(serializers.Serializer):
    category__title = serializers.CharField()
    sum_of_income = serializers.FloatField()


class SumByUserSerializer(serializers.Serializer):
    user__username = serializers.CharField()
    sum_of_income = serializers.FloatField()


class DebtOperationsSerializer(serializers.Serializer):
    pk = serializers.ListField()


class IncomeSummarySerializer(serializers.Serializer):
    sum_of_income = serializers.FloatField()
    sum_of_debt = serializers.FloatField()
    sum_of_income_by_source = SumBySourceSerializer(many=True)
    sum_of_income_by_category = SumByCategorySerializer(many=True)
    sum_of_income_by_user = SumByUserSerializer(many=True)
    list_of_debt_operations = DebtOperationsSerializer()





