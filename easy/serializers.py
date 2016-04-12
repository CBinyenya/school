__author__ = 'Monte'
from rest_framework import serializers
from easy.models import *


class StudentSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    pk = serializers.IntegerField(read_only=True)
    reg_number = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=13)
    '''school = serializers.PrimaryKeyRelatedField() ManyRelatedField(child_relation= queryset=School.objects.all(), null=True, blank=True)
    parents = serializers.ManyRelatedField(queryset=Parent.objects.all())
    stream = serializers.ManyRelatedField(queryset=Stream.objects.all(), null=True, blank=True)'''

    def update(self, instance, validated_data):
        instance.reg_number = validated_data.get('reg_number', instance.title)
        instance.phone = validated_data.get('phone', instance.title)
        instance.school = validated_data.get('school', instance.title)
        instance.parents = validated_data.get('parents', instance.title)
        instance.stream = validated_data.get('stream', instance.title)

    class Meta:
        fields = ('school', 'parents', 'stream')
        
class ExamSerializer(serializers.Serializer):
    class Meta:
        model = Exam
        fields = ("exam_name", "questions")
    

