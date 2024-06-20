from rest_framework import serializers

from .models import  Screen, Seat, Section , ShowSeatReservation


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = [
            "id",
            "row_number",
            "column_number",
           
        ]


class SectionSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "name", "rows", "price", "seats"]


class ScreenSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, required=False)

    class Meta:
        model = Screen
        fields = [
            "id",
            "name",
            "quality",
            "sound",
            "image",
            "rows",
            "cols",
            "layout",
            "sections",
            
        ]

    def create(self, validated_data):
        sections_data = validated_data.pop("sections")
        screen = Screen.objects.create(**validated_data)

        for section_data in sections_data:
            Section.objects.create(screen=screen, **section_data)

        return screen

    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections", [])
        instance.name = validated_data.get("name", instance.name)
        instance.quality = validated_data.get("quality", instance.quality)
        instance.sound = validated_data.get("sound", instance.sound)
        instance.image = validated_data.get("image", instance.image)
        instance.rows = validated_data.get("rows", instance.rows)
        instance.cols = validated_data.get("cols", instance.cols)
        instance.save()
        
        print(sections_data)
        if sections_data is not None:
            # Update or create sections and recreate layout
            existing_sections = {
                section.id: section for section in instance.sections.all()
            }
            layout = []
            for section_data in sections_data:
                section_id = section_data.get("id")
                if section_id and section_id in existing_sections:
                    section = existing_sections.pop(section_id)
                    section.name = section_data.get("name", section.name)
                    section.rows = section_data.get("rows", section.rows)
                    section.price = section_data.get("price", section.price)
                    section.save()
                else:
                    section = Section.objects.create(screen=instance, **section_data)

                for row in range(section.rows):
                    layout_row = []
                    for col in range(instance.cols):
                        seat = Seat.objects.get_or_create(
                            section=section,
                            row_number=row,
                            column_number=col,
                        )[0]
                        layout_row.append(seat.id)
                    layout.append(layout_row)

            # Delete sections that were not in the update data
            for section in existing_sections.values():
                section.delete()

            # Update layout
            instance.layout = layout
            instance.save()

        return instance


class ScreenLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['layout']


class ShowSeatReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSeatReservation
        fields = [
            "show",
            "seat",
            "reserved_by",
            "is_reserved",
            "selected_by",
            "selected_at",
        ]
