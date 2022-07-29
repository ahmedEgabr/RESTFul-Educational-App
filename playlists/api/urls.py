from django.urls import path, include
from .views import (
FavoriteController,
PlaylistList,
PlaylistLectures,
PlaylistDetailDestroy,
PlayListLectureDestroy,
WatchHistoryList
)

app_name = 'playlists'

urlpatterns = [
  # Playlists APIs routes
  path('', PlaylistList.as_view()),
  path('<int:playlist_id>', PlaylistDetailDestroy.as_view(), name='playlist-detail'),
  path('<int:playlist_id>/lectures/', PlaylistLectures.as_view(), name='playlist-lectures'),
  path('<int:playlist_id>/lectures/<int:lecture_id>', PlayListLectureDestroy.as_view(), name='remove-from-playlist'),

  # Favorites APIs routes
  path('favorites', FavoriteController.as_view(), name='favorites'),

  # History APIs
  path('watch_history/', WatchHistoryList.as_view(), name='watch_history'),

]
