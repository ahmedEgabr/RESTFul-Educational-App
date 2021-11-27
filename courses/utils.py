from .models import Content, Course
import alteby.utils as general_utils

def get_course(course_id, prefetch_related=None, select_related=None):
    try:
        query = Course.objects
        if prefetch_related:
            query =  query.prefetch_related(*prefetch_related)
        if select_related:
            query =  query.select_related(*select_related)
        return query.get(id=course_id), True, None
    except Course.DoesNotExist:
        return None, False, general_utils.errors['course_not_found']

def get_content(content_id, course_id=None, prefetch_related=None, select_related=None):
    try:
        query = Content.objects
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if select_related:
            query = query.select_related(*select_related)
        if course_id:
            query = query.get(id=content_id, course_id=course_id)
        else:
            query = query.get(id=content_id)

        return query, True, None
    except Content.DoesNotExist:
        return None, False, general_utils.errors['content_not_found']


def allowed_to_access_content(user, content):
    if content.can_access(user) or is_enrolled(user, content.course):
        return True
    return False

def allowed_to_access_course(user, course):
    if course.can_access(user) or is_enrolled(user, course):
        return True
    return False

def is_enrolled(user, course):
    return user.is_student and user.student_info.is_enrolled(course)
