from django.urls import path, include
from .views import (
CourseList, CourseUnitsList, UnitDetail, CourseIndex,
TopicList, TopicDetail, LecturesList,
FeaturedCoursesList, CourseDetail,
TrackCourseActivity,
LectureDetail, CourseDiscussions,
CourseFeedbacks, LectureDiscussions,
QuizDetail, CourseQuizAnswer, LectureQuizAnswer,
CourseQuizResult, LectureQuizResult,
CourseAttachement, LectureAttachement,
CourseTreeLecturesList, LectureExternalLinksList, LectureReferenceList, CourseReferenceList,
CourseTeachersList
)

app_name = 'courses'

urlpatterns = [
  # courses APIs routes
  path('', CourseList.as_view(), name='courses'),

  # Courses API
  path('featured/', FeaturedCoursesList.as_view(), name='featured-course'),
  path('<int:course_id>/', CourseDetail.as_view(), name='course'),
  path('<int:course_id>/index', CourseIndex.as_view(), name='course-index'),
  path('<int:course_id>/feedbacks/', CourseFeedbacks.as_view(), name='course_feedbacks'),
  path('<int:course_id>/discussions', CourseDiscussions.as_view(), name='course_discussions'),
  path('<int:course_id>/quiz', QuizDetail.as_view(), name='course_quiz'),
  path('<int:course_id>/quiz/result', CourseQuizResult.as_view(), name='course_quiz_result'),
  path('<int:course_id>/quiz/answer', CourseQuizAnswer.as_view(), name='course_quiz_answer'),
  path('<int:course_id>/attachements', CourseAttachement.as_view(), name='course_attachment'),
  path('<int:course_id>/references', CourseReferenceList.as_view(), name='course-references'),
  path('<int:course_id>/teachers', CourseTeachersList.as_view(), name='course-teachers'),

  # Units API
  path('<int:course_id>/lectures/', CourseTreeLecturesList.as_view(), name='lectures'),
  path('<int:course_id>/units/', CourseUnitsList.as_view(), name='units'),
  path('<int:course_id>/units/<int:unit_id>', UnitDetail.as_view(), name='unit'),
  # Topics API
  path('<int:course_id>/units/<int:unit_id>/topics', TopicList.as_view(), name='topics'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>', TopicDetail.as_view(), name='topic-detail'),

  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures', LecturesList.as_view(), name='lectures-list'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>', LectureDetail.as_view(), name='lecture-detail'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/mark_as_read', TrackCourseActivity.as_view(), name='mark_as_read'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/discussions', LectureDiscussions.as_view(), name='lecture_discussion'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/quiz', QuizDetail.as_view(), name='lecture_quiz'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/quiz/result', LectureQuizResult.as_view(), name='lecture_quiz_result'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/quiz/answer', LectureQuizAnswer.as_view(), name='lecture_quiz_answer'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/attachements', LectureAttachement.as_view(), name='lecture_attachment'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/external_links', LectureExternalLinksList.as_view(), name='external_links'),
  path('<int:course_id>/units/<int:unit_id>/topics/<int:topic_id>/lectures/<int:lecture_id>/references', LectureReferenceList.as_view(), name='lecture-references'),

  # Lectures API
  path('<int:course_id>/lectures/', LecturesList.as_view(), name='lectures'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>', LectureDetail.as_view(), name='lectures'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/mark_as_read', TrackCourseActivity.as_view(), name='mark_as_read'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/discussions', LectureDiscussions.as_view(), name='lectures_discussions'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/quiz', QuizDetail.as_view(), name='lectures_quiz'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/quiz/result', LectureQuizResult.as_view(), name='lectures_quiz_result'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/quiz/answer', LectureQuizAnswer.as_view(), name='lectures_quiz_answer'), # DEPRECATED
  path('<int:course_id>/lectures/<int:lectures_id>/attachements', LectureAttachement.as_view(), name='lectures_attachment'), # DEPRECATED


]
