from rest_framework import serializers

from homework.models import File, Homework, Image, Schedule


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            "image",
            "telegram_file_id",
        )


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "file",
            "telegram_file_id",
        )


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
        representation["images"] = [
            {"path": i.image.url, "telegram_file_id": i.telegram_file_id}
            for i in instance.images.all()
        ]
        representation["files"] = [
            {
                "path": i.file.url,
                "telegram_file_id": i.telegram_file_id,
                "filename": i.file_name,
            }
            for i in instance.files.all()
        ]
        return representation


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "weekday",
            "lesson",
            "subject",
        )
