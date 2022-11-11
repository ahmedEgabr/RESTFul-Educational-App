import alteby.utils as general_utils
from moviepy.editor import VideoFileClip
from datetime import datetime
import time


def get_course(course_id, prefetch_related=None, select_related=None):
    from .models import Course
    try:
        query = Course.objects
        if prefetch_related:
            query =  query.prefetch_related(*prefetch_related)
        if select_related:
            query =  query.select_related(*select_related)
        return query.get(id=course_id), True, None
    except Course.DoesNotExist:
        return None, False, general_utils.error('not_found')

def get_lecture(lecture_id, course_id=None, prefetch_related=None, select_related=None):
    from .models import Lecture
    try:
        query = Lecture.objects
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if select_related:
            query = query.select_related(*select_related)
        if course_id:
            query = query.get(id=lecture_id, course_id=course_id)
        else:
            query = query.get(id=lecture_id)

        return query, True, None
    except Lecture.DoesNotExist:
        return None, False, general_utils.error('not_found')

def get_unit(filter_kwargs, prefetch_related=None, select_related=None):
    from .models import Unit
    try:
        query = Unit.objects
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if select_related:
            query = query.select_related(*select_related)
        return query.get(**filter_kwargs), True, None
    except Unit.DoesNotExist:
        return None, False, general_utils.error('not_found')


def get_object(model, filter_kwargs, prefetch_related=None, select_related=None):
    try:
        query = model.objects
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if select_related:
            query = query.select_related(*select_related)
        return query.get(**filter_kwargs), True, None
    except model.DoesNotExist:
        return None, False, general_utils.error('not_found')


def get_resolution(quality):
    if quality == 144:
        return True, 176, 144
    elif quality == 240:
        return True, 426, 240
    elif quality == 360:
        return True, 640, 360
    elif quality == 480:
        return True, 854, 480
    elif quality == 720:
        return True, 1280, 720
    elif quality == 1080:
        return True, 1920, 1080
    elif quality == 1440:
        return True, 2560, 1440
    elif quality == 2160:
        return True, 3840, 2160
    return False, 0, 0

# this function is for initializing lecture path
def get_lecture_path(instance, filename):
    today = datetime.today().strftime("%d-%m-%Y")

    file_extension = filename.split(".")[-1]
    
    return 'videos/lectures/{0}/{1}.{2}'.format(
        today,
        int(time.time()), 
        file_extension.lower()
    )