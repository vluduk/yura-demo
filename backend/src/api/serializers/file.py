from rest_framework import serializers
from api.models.file import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('id', 'file', 'filename', 'file_size', 'content_type', 'created_at')
        read_only_fields = ('id', 'created_at', 'filename', 'file_size', 'content_type')

    def create(self, validated_data):
        file_obj = validated_data['file']
        validated_data['filename'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        validated_data['content_type'] = file_obj.content_type
        return super().create(validated_data)
