import sys
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from alteby.permissions import CoursePermission
from rest_framework import status
from django.utils import timezone
from users.api.serializers import TeacherSerializer
from .serializers import (
CourseSerializer, CoursesSerializer, CourseIndexSerialiser,
UnitSerializer, TopicsListSerializer,
TopicDetailSerializer, DemoLectureSerializer,
FullLectureSerializer, QuizSerializer,
QuizResultSerializer, AttachementSerializer,
DiscussionSerializer, FeedbackSerializer,
LectureExternalLinkSerializer, ReferenceSerializer, CoursePricingPlanSerializer
)
from courses.models import Course, Unit, Topic, CourseActivity, Lecture, Discussion, Feedback, Privacy
from question_banks.models import Question, Choice, QuestionAnswer
from playlists.models import WatchHistory
from functools import reduce
import operator
import courses.utils as utils
import alteby.utils as general_utils
from django.db import IntegrityError
from rest_framework.generics import ListAPIView
from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Prefetch, Count, Sum, OuterRef, Exists, Subquery, IntegerField, Q, FloatField
from payment.models import CourseEnrollment
from .swagger_schema import course_detail_swagger_schema
from categories.models import Category
from categories.api.serializers import CategorySerializer
from django_currentuser.middleware import get_current_authenticated_user

class SearchView(APIView, PageNumberPagination):
    
    search_types=["courses", "units", "topics", "lectures", "categories", "teachers"]
    
    def get(self, request):
        request_params = self.request.GET
        search_type = request_params.get('type', None)
        search_term = request_params.get('search_term', None)
        
        if not search_type and not search_term:
            courses = self.get_courses(request, all=True)
            return self.get_paginated_response(courses)
        
        
        if search_type not in self.search_types:
            return Response(
                general_utils.error('invalid_search_type', search_types=self.search_types), 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not search_term:
            result = getattr(self, "get_%s" % search_type, None)(request, all=True)
        else:            
            result = getattr(self, "get_%s" % search_type, None)(request, search_term)
        return self.get_paginated_response(result)
    
    def get_courses(self, request, search_term=None, all=False):
        courses_queryset = Course.get_allowed_courses(user=self.request.user).prefetch_related(
                'tags', 'privacy__shared_with', 'units'
                ).select_related('privacy')

        if not all:
            search_query = reduce(
                operator.or_, (
                    Q(title__icontains=word) | 
                    Q(description__icontains=word) for word in search_term.split(" ")
                    )
                )
            
            courses_queryset = courses_queryset.filter(search_query)
        
        courses = self.paginate_queryset(courses_queryset, request, view=self)
        serializer = CoursesSerializer(courses, many=True, context={'request': request})
        return serializer.data
    
    def get_units(self, request, search_term=None, all=False):

        allowed_courses = Course.get_allowed_courses(user=self.request.user)
        
        # Sub query of lectures_queryset
        topics_queryset = Topic.objects.filter(
            unit=OuterRef(OuterRef(OuterRef('pk')))
            ).values_list('pk')

        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__in=topics_queryset
            ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
            user=request.user,
            lecture__in=lectures_queryset,
            is_finished=True
            )

        # Main SQL Query to execute
        queryset = Unit.objects.annotate(
            lectures_count=Count('topics__assigned_lectures', distinct=True),
            lectures_duration=Coalesce(Sum('topics__assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset)),
        ).exclude(
            ~Q(course__in=allowed_courses)
        )
        
        if all:
            units = queryset.all()
        else:
            search_query = reduce(
                operator.or_, (
                    Q(title__icontains=word) for word in search_term.split(" ")
                    )
            )
            units = queryset = queryset.filter(search_query)

        units = self.paginate_queryset(units, request, view=self)
        serializer = UnitSerializer(units, many=True, context={'request': request})
        return serializer.data
    
    def get_topics(self, request, search_term=None, all=False):

        allowed_courses = Course.get_allowed_courses(user=self.request.user)
        
        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__id=OuterRef(OuterRef('pk'))
            ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
            user=request.user,
            lecture__in=lectures_queryset,
            is_finished=True
            )

        # Main SQL Query to execute
        queryset = Topic.objects.annotate(
            lectures_count=Count('assigned_lectures', distinct=True),
            lectures_duration=Coalesce(Sum('assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset))
            ).exclude(
                ~Q(unit__course__in=allowed_courses)
            )

        if all:
            topics = queryset.all()
        else:
            search_query = reduce(
                operator.or_, (
                    Q(title__icontains=word) for word in search_term.split(" ")
                    )
            )
            topics = queryset = queryset.filter(search_query)
            
        topics = self.paginate_queryset(topics, request, view=self)
        serializer = TopicsListSerializer(topics, many=True, context={'request': request})
        return serializer.data
    
    def get_lectures(self, request, search_term=None, all=False):
        allowed_courses = Course.get_allowed_courses(user=self.request.user)
        queryset = lectures = Lecture.objects.select_related('privacy').prefetch_related('privacy__shared_with').annotate(
                    viewed=Exists(
                                CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                                ),
                    left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=request.user).values('left_off_at')), 0, output_field=FloatField())
            ).exclude(
                ~Q(assigned_topics__topic__unit__course__in=allowed_courses)
            )
        if all:
            lectures = queryset.all()
        else:
            search_query = reduce(
                operator.or_, (
                    Q(title__icontains=word) |
                    Q(description__icontains=word) for word in search_term.split(" ")
                    )
            )
            lectures = queryset.filter(search_query)
        lectures = self.paginate_queryset(lectures, request, view=self)
        serializer = DemoLectureSerializer(lectures, many=True, context={'request': request})
        return serializer.data
    
    def get_categories(self, request, search_term=None, all=False):
        
        if all:
            categories = Category.objects.all()
        else:
            search_query = reduce(
                operator.or_, (
                    Q(name__icontains=word) for word in search_term.split(" ")
                    )
                )
            categories = Category.objects.filter(search_query)
        
        categories = self.paginate_queryset(categories, request, view=self)
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return serializer.data
    
    def get_teachers(self, request, search_term=None, all=False):
        return None
        
    
class CourseList(ListAPIView):
    serializer_class = CoursesSerializer

    def get_queryset(self):
        request_params = self.request.GET
        queryset = Course.get_allowed_courses(user=self.request.user).prefetch_related(
            'tags', 'privacy__shared_with', 'units'
        ).select_related('privacy')
           
        if 'q' in request_params:
            search_query = request_params.get('q').split(" ")
            query = reduce(operator.or_, (Q(title__icontains=search_term) | Q(description__icontains=search_term) for search_term in search_query))
            serializer = self.get_serializer()
            return serializer.get_related_queries(queryset.filter(query))
        else:
            serializer = self.get_serializer()
            return serializer.get_related_queries(queryset)


class FeaturedCoursesList(ListAPIView):
    serializer_class = CoursesSerializer

    def get_queryset(self):
        queryset = Course.get_allowed_courses(user=self.request.user).filter(
            featured=True
        ).prefetch_related(
            'tags', 'privacy__shared_with', 'units'
        ).select_related('privacy')

        serializer = self.get_serializer()
        return serializer.get_related_queries(queryset)


class CourseDetail(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    @course_detail_swagger_schema
    def get(self, request, course_id, format=None):

        course = Course.objects.prefetch_related(
        'privacy__shared_with', 'categories__course_set').select_related('privacy').filter(
            id=course_id
        ).last()
        if not course:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, many=False, context={'request': request})
        return Response(serializer.data)


class CourseIndex(APIView):

    def get(self, request, course_id, format=None):

        filter_kwargs = {
            'id': course_id,
            'is_active': True
        }
        prefetch_lectures = Prefetch(
            'units__topics__assigned_lectures__lecture',
            queryset=Lecture.objects.select_related(
                'privacy'
                ).prefetch_related(
                    'privacy__shared_with'
                    ).annotate(
                        is_enrolled=Exists(
                            CourseEnrollment.objects.filter(
                                Q(lifetime_enrollment=True) |
                                Q(expiry_date__gt=timezone.now()),
                                course=course_id, 
                                user=request.user,
                                force_expiry=False,
                                is_active=True
                                )
                            )
                        )
                    )
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs, prefetch_related=['units__topics',  prefetch_lectures])
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseIndexSerialiser(course, many=False, context={'request': request, 'user': request.user})
        return Response(serializer.data)


class LectureDetail(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id, format=None):
        allowed_courses = Course.get_allowed_courses(user=self.request.user)
        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }

        lecture = Lecture.objects.select_related('privacy').prefetch_related('privacy__shared_with').annotate(
                viewed=Exists(
                            CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                            ),
                left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user).values('left_off_at')), 0, output_field=FloatField())
        ).filter(**filter_kwargs).exclude(
            ~Q(assigned_topics__topic__unit__course__in=allowed_courses)
        ).first()
        
        if not lecture:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            serializer = FullLectureSerializer(lecture, many=False, context={'request': request})
            watch_history, created = WatchHistory.objects.get_or_create(user=request.user)
            watch_history.add(lecture)
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class CourseUnitsList(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):
        course, found, error = utils.get_course(course_id)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        
        # Sub query of lectures_queryset
        topics_queryset = Topic.objects.filter(
            unit=OuterRef(OuterRef('pk'))
            ).values_list('pk')

        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__in=topics_queryset
            ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
                user=request.user,
                lecture__assigned_topics__topic__in=topics_queryset,
                is_finished=True
            )

        # Main SQL Query to execute
        units = course.units.annotate(
            lectures_count=Coalesce(Count('topics__assigned_lectures', distinct=True), 0, output_field=IntegerField()),
            lectures_duration=Coalesce(Sum('topics__assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset))
            ).order_by("pk")

        units = self.paginate_queryset(units, request, view=self)
        serializer = UnitSerializer(units, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class UnitDetail(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, format=None):

        # Sub query of lectures_queryset
        topics_queryset = Topic.objects.filter(
            unit=OuterRef(OuterRef('pk'))
            ).values_list('pk')

        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__in=topics_queryset
            ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
            user=request.user,
            lecture__assigned_topics__topic__in=topics_queryset,
            is_finished=True
            )

        # Main SQL Query to execute
        unit = Unit.objects.annotate(
            lectures_count=Count('topics__assigned_lectures', distinct=True),
            lectures_duration=Coalesce(Sum('topics__assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset))
            ).filter(id=unit_id, course_id=course_id).last()

        serializer = UnitSerializer(unit, many=False, context={'request': request})
        return Response(serializer.data)

class TopicList(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, format=None):
        filter_kwargs = {
            'id': unit_id,
            'course__id': course_id
        }
        unit, found, error = utils.get_object(model=Unit, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)


        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__id=OuterRef(OuterRef('pk'))
        ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
            user=request.user,
            lecture__in=lectures_queryset,
            is_finished=True
        )

        # Main SQL Query to execute
        topics = unit.topics.annotate(
            lectures_count=Count('assigned_lectures', distinct=True),
            lectures_duration=Coalesce(Sum('assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset))
        )

        topics = self.paginate_queryset(topics, request, view=self)
        serializer = TopicsListSerializer(topics, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TopicDetail(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, format=None):
        filter_kwargs = {
            'id': topic_id,
            'unit__course__id': course_id,
            'unit__id': unit_id
        }

        # Sub query of course_activity_queryset
        lectures_queryset = Lecture.objects.filter(
            assigned_topics__topic__id=OuterRef(OuterRef('pk'))
        ).values_list('pk')

        # Sub query of the main SQL query
        course_activity_queryset = CourseActivity.objects.filter(
            user=request.user,
            lecture__in=lectures_queryset,
            is_finished=True
        )

        # Main SQL Query to execute
        topic = Topic.objects.annotate(
            lectures_count=Count('assigned_lectures', distinct=True),
            lectures_duration=Coalesce(Sum('assigned_lectures__lecture__duration'), 0, output_field=FloatField()),
            num_of_lectures_viewed=general_utils.SQCount(Subquery(course_activity_queryset))
        ).filter(**filter_kwargs).last()
        
        if not topic:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        serializer = TopicDetailSerializer(topic, many=False, context={'request': request})
        return Response(serializer.data)

class LecturesList(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, format=None):
        
        lectures = Lecture.objects.select_related('privacy').prefetch_related('privacy__shared_with').annotate(
                viewed=Exists(
                            CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                            ),
                left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user).values('left_off_at')), 0, output_field=FloatField())
        ).filter(
            assigned_topics__topic__id=topic_id,
            assigned_topics__topic__unit__course__id=course_id,
            assigned_topics__topic__unit__id=unit_id,
            ).order_by("assigned_topics__order")
        
        lectures = self.paginate_queryset(lectures, request, view=self)
        serializer = DemoLectureSerializer(lectures, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class CourseTreeLecturesList(APIView, PageNumberPagination):

    def get(self, request, course_id, format=None):
        allowed_courses = Course.get_allowed_courses(user=self.request.user)
        lectures_ids = request.data.get("lectures_ids")
        if not isinstance(lectures_ids, list):
            error = general_utils.error('required_fields')
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        lectures = Lecture.objects.select_related('privacy').prefetch_related('privacy__shared_with').annotate(
            viewed=Exists(
                        CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user, is_finished=True)
                        ),
            left_off_at=Coalesce(Subquery(CourseActivity.objects.filter(lecture=OuterRef('pk'), user=self.request.user).values('left_off_at')), 0, output_field=FloatField())
        ).filter(
            ~Q(assigned_topics__topic__unit__course__in=allowed_courses),
            id__in=lectures_ids
        )
        lectures = self.paginate_queryset(lectures, request, view=self)
        serializer = DemoLectureSerializer(lectures, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class QuizDetail(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id=None, topic_id=None, lecture_id=None, format=None):

        request_params = self.request.GET
        retake = 0
        if 'retake' in request_params:
            retake = int(request_params.get('retake'))

        if lecture_id:
            filter_kwargs = {
                'id': lecture_id,
                'assigned_topics__topic__id': topic_id,
                'assigned_topics__topic__unit__id': unit_id,
                'assigned_topics__topic__unit__course__id': course_id,
                'assigned_topics__topic__unit__course__is_active': True
            }
            lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs, select_related=['quiz'])
            if not found:
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            if not lecture.is_allowed_to_access_lecture(request.user):
                error = general_utils.error('access_denied')
                return Response(error, status=status.HTTP_403_FORBIDDEN)

            if not lecture.quiz:
                error = general_utils.error('not_found')
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            serializer = QuizSerializer(lecture.quiz, many=False, context={'request': request})

            # Delete previous result of this quiz
            if retake:
                QuestionAnswer.objects.filter(user=request.user, quiz=lecture.quiz).delete()
            return Response(serializer.data)

        else:
            filter_kwargs = {
                'id': course_id,
                'is_active': True
            }
            course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs, select_related=['quiz'], prefetch_related=['quiz__questions__choices'])
            if not found:
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            if not course.quiz:
                error = general_utils.error('not_found')
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            serializer = QuizSerializer(course.quiz, many=False, context={'request': request})

            # Delete previous result of this quiz
            if retake:
                QuestionAnswer.objects.filter(user=request.user, quiz=course.quiz).delete()

            return Response(serializer.data)

class CourseQuizAnswer(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    @transaction.atomic
    def put(self, request, course_id, format=None):

        request_body = request.data
        if 'quiz_answers' not in request_body:
            return Response(general_utils.error('required_fields'), status=status.HTTP_400_BAD_REQUEST)

        quiz_answers = request_body['quiz_answers']

        filter_kwargs = {
            'id': course_id,
            'is_active': True
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        quiz = course.quiz
        if not quiz:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        answers_objs = []
        for answer in quiz_answers:
            try:
                question = Question.objects.get(id=answer['question_id'])
                selected_choice = Choice.objects.get(id=answer['selected_choice_id'], question=question)
            except Question.DoesNotExist:
                return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)
            except Choice.DoesNotExist:
                return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

            answer = QuestionAnswer(user=request.user, quiz=quiz, question=question, selected_choice=selected_choice, is_correct=selected_choice.is_correct)
            answers_objs.append(answer)

        if not answers_objs:
            return Response(general_utils.error('empty_quiz_answers'), status=status.HTTP_400_BAD_REQUEST)

        QuestionAnswer.objects.bulk_create(answers_objs)
        return Response(general_utils.success('quiz_answer_submitted'), status=status.HTTP_201_CREATED)

class LectureQuizAnswer(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    @transaction.atomic
    def put(self, request, course_id, unit_id, topic_id, lecture_id, format=None):

        request_body = request.data
        if 'quiz_answers' not in request_body:
            return Response(general_utils.error('required_fields'), status=status.HTTP_400_BAD_REQUEST)

        quiz_answers = request_body['quiz_answers']

        filter_kwargs = {
            'id': lecture_id,
            'topic__id': topic_id,
            'topic__unit__id': unit_id,
            'topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs, select_related=['quiz'])
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        quiz = lecture.quiz
        if not quiz:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        answers_objs = []
        for answer in quiz_answers:
            user = request.user
            try:
                question = Question.objects.get(id=answer['question_id'])
                selected_choice = Choice.objects.get(id=answer['selected_choice_id'], question=question)
            except (Question.DoesNotExist, Choice.DoesNotExist):
                return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)
            
            answer = QuestionAnswer(user=request.user, quiz=quiz, question=question, selected_choice=selected_choice)
            answers_objs.append(answer)

        if not answers_objs:
            return Response(general_utils.error('empty_quiz_answers'), status=status.HTTP_400_BAD_REQUEST)

        QuestionAnswer.objects.bulk_create(answers_objs)
        return Response(general_utils.success('quiz_answer_submitted'), status=status.HTTP_201_CREATED)

class CourseQuizResult(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id):

        filter_kwargs = {
            'id': course_id,
            'is_active': True
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs, prefetch_related=['quiz__questions'], select_related=['quiz'])
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        quiz = course.quiz
        if not quiz:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        serializer = QuizResultSerializer(quiz, many=False, context={'request': request})
        return Response(serializer.data)


class LectureQuizResult(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id):

        filter_kwargs = {
            'id': lecture_id,
            'topic__id': topic_id,
            'topic__unit__id': unit_id,
            'topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        quiz = lecture.quiz
        if not quiz:
            return Response(general_utils.error('not_found'), status=status.HTTP_404_NOT_FOUND)

        serializer = QuizResultSerializer(quiz, many=False, context={'request': request})
        return Response(serializer.data)

class CourseAttachement(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):
        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if course.is_allowed_to_access_course(request.user):
            attachments = course.attachments.all()

            serializer = AttachementSerializer(attachments, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)

class LectureAttachement(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id, format=None):

        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            attachments = lecture.attachments.all()
            serializer = AttachementSerializer(attachments, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class LectureExternalLinksList(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id, format=None):

        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            external_links = lecture.external_links.all()
            serializer = LectureExternalLinkSerializer(external_links, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class LectureReferenceList(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id, format=None):

        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            references = lecture.references.all()
            serializer = ReferenceSerializer(references, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class CourseReferenceList(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):

        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if course.is_allowed_to_access_course(request.user):
            references = course.references
            serializer = ReferenceSerializer(references, many=True, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class CourseTeachersList(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):

        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if course.is_allowed_to_access_course(request.user):
            teachers = course.get_contributed_teachers()
            serializer = TeacherSerializer(teachers, many=True)
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class CourseDiscussions(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):

        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        
        discussions = course.discussions.all()
        serializer = DiscussionSerializer(discussions, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, course_id, format=None):

        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if course.is_allowed_to_access_course(request.user):
            discussion_body = request.data['body']
            discussion = Discussion.objects.create(
            user=request.user,
            object=course,
            body=discussion_body
            )
            serializer = DiscussionSerializer(discussion, many=False, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class LectureDiscussions(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, unit_id, topic_id, lecture_id, format=None):

        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs, prefetch_related=['privacy'])
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            discussions = lecture.discussions.all()
            discussions = self.paginate_queryset(discussions, request, view=self)
            serializer = DiscussionSerializer(discussions, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)

    def post(self, request, course_id, unit_id, topic_id, lecture_id, format=None):
        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if lecture.is_allowed_to_access_lecture(request.user):
            discussion_body = request.data['body']
            discussion = Discussion.objects.create(
            user=request.user,
            object=lecture,
            body=discussion_body
            )
            serializer = DiscussionSerializer(discussion, many=False, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)



class CourseFeedbacks(APIView, PageNumberPagination):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id, format=None):
        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        feedbacks = course.feedbacks.all()
        feedbacks = self.paginate_queryset(feedbacks, request, view=self)
        serializer = FeedbackSerializer(feedbacks, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


    def post(self, request, course_id, format=None):
        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if course.is_allowed_to_access_course(request.user):
            rating = request.data['rating']
            description = request.data['description']
            try:
                feedback = Feedback.objects.create(user=request.user, course=course, rating=rating, description=description)
            except IntegrityError as e:
                response = {
                    'status': 'error',
                    'message': str(e),
                    'error_description': 'Ensure that rating value is less than or equal to 5 and more than or equal to 1.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            serializer = FeedbackSerializer(feedback, many=False, context={'request': request})
            return Response(serializer.data)

        return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)


class TrackCourseActivity(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def post(self, request, course_id, unit_id, topic_id, lecture_id, format=None):
        filter_kwargs = {
            'id': lecture_id,
            'assigned_topics__topic__id': topic_id,
            'assigned_topics__topic__unit__id': unit_id,
            'assigned_topics__topic__unit__course__id': course_id
        }
        lecture, found, error = utils.get_object(model=Lecture, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        if not lecture.is_allowed_to_access_lecture(request.user):
            return Response(general_utils.error('access_denied'), status=status.HTTP_403_FORBIDDEN)

        lecture_activity, created = CourseActivity.objects.get_or_create(user=request.user, lecture=lecture)

        update_fields = []
        if 'left_off_at' in request.data:
            left_off_at = request.data['left_off_at']

            if not isinstance(left_off_at, (float, int)) or left_off_at < 0:
                return Response(general_utils.error('incorrect_left_off'), status=status.HTTP_400_BAD_REQUEST)

            lecture_activity.left_off_at = left_off_at
            update_fields.append('left_off_at')

        if 'is_finished' in request.data:
            is_finished = request.data['is_finished']
            if not isinstance(is_finished, bool):
                return Response(general_utils.error('incorrect_is_finished'), status=status.HTTP_400_BAD_REQUEST)

            lecture_activity.is_finished = is_finished
            update_fields.append('is_finished')


        lecture_activity.save(update_fields=update_fields)

        response = {
            'status': 'success',
            'message': 'Checked!',
            'success_description': 'This Lecture Marked as read.'
        }
        return Response(response, status=status.HTTP_201_CREATED)

class CoursePricingPlanList(APIView, PageNumberPagination):
    
    def get(self, request, course_id):
        
        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs)
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        
        pricing_plans = course.get_pricing_plans(request)
        pricing_plans = self.paginate_queryset(pricing_plans, request, view=self)
        serializer = CoursePricingPlanSerializer(pricing_plans, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    

class CourseEnrollmentView(APIView):
    permission_classes = (IsAuthenticated, CoursePermission)
    def get(self, request, course_id):
        filter_kwargs = {
            'id': course_id
        }
        course, found, error = utils.get_object(model=Course, filter_kwargs=filter_kwargs, select_related=["privacy"])
        if not found:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        
        if not course.is_allowed_to_access_course(request.user):
            return Response(general_utils.error('access_denied'), status=status.HTTP_402_PAYMENT_REQUIRED)
        
        is_enrolled = course.enroll(user=request.user)
        
        if not is_enrolled:
            return Response(general_utils.error('cannot_enroll'), status=status.HTTP_402_PAYMENT_REQUIRED)
        
        return Response(general_utils.success('enrolled'), status=status.HTTP_201_CREATED)
    