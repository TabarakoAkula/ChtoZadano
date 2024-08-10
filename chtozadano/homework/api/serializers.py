from rest_framework import serializers

from homework.models import File, Homework, Image, Schedule


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("file",)


class HomeworkSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    files = FileSerializer(many=True)

    class Meta:
        model = Homework
        fields = (
            "id",
            "description",
            "subject",
            "group",
            "created_at",
            "author",
            "images",
            "files",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["images"] = [i.image.url for i in instance.images.all()]
        representation["files"] = [i.file.url for i in instance.files.all()]
        return representation


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "weekday",
            "lesson",
            "subject",
        )
