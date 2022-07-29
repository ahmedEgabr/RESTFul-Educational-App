from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .serializers import PlaylistSerializer, FavoriteSerializer, WatchHistorySerializer
from playlists.models import Playlist, Favorite, WatchHistory
from courses.api.serializers import DemoLectureSerializer, FullLectureSerializer
from courses.models import Lecture, CourseActivity
import courses.utils as utils
import alteby.utils as general_utils
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Exists, Subquery, FloatField
from django.db.models.functions import Coalesce

class PlaylistList(APIView, PageNumberPagination):
    """
    List all playlists, or create a new playlist.
    """

    def get(self, request, format=None):
        playlists = Playlist.objects.prefetch_related('lectures').filter(user=request.user)
        playlists = self.paginate_queryset(playlists, request, view=self)
        serializer = PlaylistSerializer(playlists, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        return self.create(request)

    def create(self, request):
        playlist_data = request.data
        playlist_data['user'] = request.user.id
        serializer = PlaylistSerializer(data=playlist_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(general_utils.success("playlist_created"), status=status.HTTP_201_CREATED)
        return Response(general_utils.error("playlist_exists"), status=status.HTTP_409_CONFLICT)


class PlaylistDetailDestroy(APIView):

    def get(self, request, playlist_id):

        playlist = Playlist.objects.filter(id=playlist_id, user=request.user).first()
        if not playlist:
            return Response(general_utils.error("not_found"), status=status.HTTP_404_NOT_FOUND)

        serializer = PlaylistSerializer(playlist, many=False, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, playlist_id, format=None):

        playlist = Playlist.objects.filter(id=playlist_id, user=request.user).first()
        if not playlist:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        playlist.delete()
        return Response(general_utils.success("deleted"))

class PlaylistLectures(APIView, PageNumberPagination):

    """
    List all playlist's lectures.
    """

    def get(self, request, playlist_id, format=None):

        playlist = Playlist.objects.filter(id=playlist_id, user=request.user).first()
        if not playlist:
            return Response(general_utils.error("not_found"), status=status.HTTP_404_NOT_FOUND)

        lectures = playlist.lectures.all().prefetch_related('privacy__shared_with').annotate(
                viewed=Exists(
                            CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                            ),
                left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user).values('left_off_at')), 0, output_field=FloatField())
        ).all()
        lectures = self.paginate_queryset(lectures, request, view=self)
        serializer = DemoLectureSerializer(lectures, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    """
    Add lecture to a playlist
    """

    def put(self, request, playlist_id, format=None):

        try:
            request_body = request.data
            lecture_id = request_body['lecture_id']
        except Exception as e:
            return Response(general_utils.error('required_fields'), status=status.HTTP_400_BAD_REQUEST)

        filter_kwargs = {
        'id': lecture_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):

            playlist = Playlist.objects.filter(id=playlist_id, user=request.user).first()
            if not playlist:
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            playlist.add(lecture)
            return Response(general_utils.success("added_to_playlist"))

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class PlayListLectureDestroy(APIView):

    """
    Remove a lecture from a playlist
    """

    def delete(self, request, playlist_id, lecture_id, format=None):

        playlist = Playlist.objects.filter(id=playlist_id, user=request.user).first()
        if not playlist:
            return Response(general_utils.error("not_found"), status=status.HTTP_404_NOT_FOUND)

        filter_kwargs = {
        'id': lecture_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        playlist.remove(lecture)
        return Response(general_utils.success("deleted"))


class FavoriteController(APIView):

    """
    List all lecture of favorites
    """

    def get(self, request, format=None):
        favorites, created = Favorite.objects.get_or_create(user=request.user)
        lectures = favorites.lectures.prefetch_related('privacy__shared_with')
        lectures = self.paginate_queryset(lectures, request, view=self)
        serializer = DemoLectureSerializer(lectures, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


    """
    Add or delete lecture from favorite
    """

    def put(self, request, format=None):
        try:
            request_body = request.data
            lecture_id = request_body['lecture_id']
        except Exception as e:
            return Response(general_utils.error('required_fields'), status=status.HTTP_400_BAD_REQUEST)


        filter_kwargs = {
        'id': lecture_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        access_granted = lecture.is_allowed_to_access_lecture(request.user)
        if access_granted:
            favorites = self.get_favorite_playlist(request)
            favorites.add(lecture)
            serializer = FavoriteSerializer(favorites, many=False, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, lecture_id, format=None):

        filter_kwargs = {
        'id': lecture_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        favorites = self.get_favorite_playlist(request)
        favorites.remove(lecture)
        serializer = FavoriteSerializer(favorites, many=False, context={'request': request})
        return Response(serializer.data)


    def get_favorite_playlist(self, request):
        favorites, created =  Favorite.objects.get_or_create(user=request.user)
        return favorites


class WatchHistoryList(APIView, PageNumberPagination):

    def get(self, request, format=None):
        user_watch_history, created = WatchHistory.objects.get_or_create(user=request.user)
        user_watch_history_lectures = user_watch_history.lectures.prefetch_related('privacy__shared_with').annotate(
                viewed=Exists(
                            CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                            ),
                left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user).values('left_off_at')), 0, output_field=FloatField())
        ).all()

        user_watch_history_lectures = self.paginate_queryset(user_watch_history_lectures, request, view=self)
        serializer = DemoLectureSerializer(user_watch_history_lectures, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
