from dal import autocomplete
from .models import Reference, Topic
from alteby.permissions import StafUserRequiredMixin
from django_currentuser.middleware import get_current_authenticated_user


class ReferenceAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        reference_category = self.forwarded.get('reference_category', None)
        qs = None
        if reference_category:
            qs = Reference.objects.filter(categories__in=[reference_category])
        return qs

class TopicAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        course = self.forwarded.get('course', None)
        qs = None
        if course:
            if self.request.user.is_superuser:
                qs = Topic.objects.filter(unit__course__id=course)
            else:
                qs = Topic.objects.filter(unit__course__id=course, created_by=self.request.user)

            if self.q:
                qs = qs.filter(title__icontains=self.q)
        return qs
