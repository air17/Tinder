from django.db.models.expressions import RawSQL
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import ProfileSerializer, ThinProfileSerializer, \
    LocationSerializer, UserSerializer, ProfileRegistrationSerializer


class ProfileViewSet(ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        """Returns a queryset with all users excluding current user
        sorted by distance from current user
        """
        profile = self.request.user.userprofile
        queryset = self.annotate_distance(UserProfile.objects.exclude(pk=profile.pk), profile)
        return queryset.order_by("distance")

    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires."""

        if self.action == "retrieve":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """Returns a list of all users except current user"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ThinProfileSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Returns a user profile"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def matches(self, request):
        """Returns matched profiles for the current user"""
        profile = self.request.user.userprofile
        queryset = profile.matched.all() | profile.matched_related.all()
        queryset = self.annotate_distance(queryset, profile)
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["put"])
    def dislike(self, request, pk):
        """Adds a user to disliked by the current user and removes from liked and matched"""
        profile = request.user.userprofile
        if profile.pk == pk:
            return Response(status=400)
        profile.matched.remove(pk)
        profile.matched_related.remove(pk)
        profile.liked.remove(pk)
        profile.disliked.add(pk)
        return Response()

    @action(detail=True, methods=["put"])
    def like(self, request, pk):
        """Adds a user to liked by the current user and adds a match if its mutual"""
        instance = self.get_object()
        profile = request.user.userprofile
        if profile == instance:
            return Response(status=400)
        profile.disliked.remove(pk)
        profile.liked.add(pk)
        if instance.liked.filter(pk=profile.pk).exists():
            profile.matched.add(pk)
        return Response()

    @staticmethod
    def annotate_distance(queryset, user):
        """Annotates queryset with a distance, using the great circle distance formula"""
        gcd_sql = "6371 * acos(least(greatest(\
        cos(radians(%s)) * cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)) \
        , -1), 1))"

        distance_raw_sql = RawSQL(
            gcd_sql,
            (user.latitude, user.longitude, user.latitude)
        )
        return queryset.annotate(distance=distance_raw_sql)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def set_location(request):
    """Saves current user's current location"""
    profile = request.user.userprofile
    serializer = LocationSerializer(profile, request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(status=400)
    return Response()


@api_view(["POST"])
def register(request):
    """Creates user profile"""
    user_serializer = UserSerializer(data=request.data)
    if user_serializer.is_valid():
        user = user_serializer.save()
    else:
        print(user_serializer.errors)
        return Response(status=400)

    request.data["user"] = user.pk
    profile_serializer = ProfileRegistrationSerializer(data=request.data)
    if profile_serializer.is_valid():
        profile_serializer.save()
    else:
        print(profile_serializer.errors)
        user.delete()
        return Response(status=400)

    return Response(get_tokens_for_user(user))


def get_tokens_for_user(user):
    """Returns auth token for a user"""
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
