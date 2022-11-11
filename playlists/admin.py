from django.contrib import admin
from alteby.admin_sites import main_admin
from .models import Playlist, Favorite, WatchHistory


main_admin.register(Playlist)
main_admin.register(Favorite)
main_admin.register(WatchHistory)
