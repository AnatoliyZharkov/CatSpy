import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cat, Mission, Target
from .serializers import CatSerializer, MissionSerializer, TargetSerializer


CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


def validate_breed(breed: str) -> bool:
    response = requests.get(CAT_API_URL, timeout=5)
    response.raise_for_status()
    breeds = {b["name"].lower() for b in response.json()}
    return breed.lower() in breeds


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

    def create(self, request, *args, **kwargs):
        if not validate_breed(request.data.get("breed", "")):
            return Response(
                {"error": "Invalid cat breed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Allow only salary update
        if set(request.data.keys()) != {"salary"}:
            return Response(
                {"error": "Only salary can be updated"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def create(self, request, *args, **kwargs):
        targets = request.data.get("targets", [])

        if not (1 <= len(targets) <= 3):
            return Response(
                {"error": "Mission must have 1 to 3 targets"},
                status=status.HTTP_400_BAD_REQUEST
            )

        mission = Mission.objects.create()

        for t in targets:
            Target.objects.create(
                mission=mission,
                name=t["name"],
                country=t["country"],
                notes=t.get("notes", "")
            )

        return Response(
            MissionSerializer(mission).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()

        if mission.cat:
            return Response(
                {"error": "Cannot delete assigned mission"},
                status=status.HTTP_400_BAD_REQUEST
            )

        mission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def assign_cat(self, request, pk=None):
        mission = self.get_object()
        cat_id = request.data.get("cat_id")

        try:
            cat = Cat.objects.get(id=cat_id)
        except Cat.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if mission.cat:
            return Response(
                {"error": "Mission already assigned"},
                status=status.HTTP_409_CONFLICT
            )

        if hasattr(cat, "mission"):
            return Response(
                {"error": "Cat already has a mission"},
                status=status.HTTP_409_CONFLICT
            )

        mission.cat = cat
        mission.save()
        return Response(status=status.HTTP_200_OK)


class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def update(self, request, *args, **kwargs):
        target = self.get_object()

        if target.is_completed or target.mission.is_completed:
            return Response(
                {"error": "Target or mission is completed. Notes are frozen."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
