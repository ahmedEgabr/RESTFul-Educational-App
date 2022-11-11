from dal import autocomplete
from .models import Reference, Topic, Unit
from alteby.permissions import StafUserRequiredMixin


class ReferenceAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        reference_category = self.forwarded.get('reference_category', None)
        qs = Reference.objects.none()
        if reference_category:
            qs = Reference.objects.filter(categories__in=[reference_category])
        else:
            qs = Reference.objects.all()
        
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class UnitsAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        course = self.forwarded.get('course', None)
        qs = Unit.objects.none()
        if course:
            if self.request.user.is_superuser or (self.request.user.is_staff and not self.request.user.is_teacher):
                qs = Unit.objects.filter(course__id=course)
            elif self.request.user.is_teacher:
                qs = Unit.objects.filter(course__id=course, created_by=self.request.user)

            if self.q:
                qs = qs.filter(title__icontains=self.q)
        return qs
    
    
class TopicsAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        unit = self.forwarded.get('unit', None)
        qs = Topic.objects.none()
        if unit:
            if self.request.user.is_superuser or (self.request.user.is_staff and not self.request.user.is_teacher):
                qs = Topic.objects.filter(unit__id=unit)
            elif self.request.user.is_teacher:
                qs = Topic.objects.filter(unit__id=unit, created_by=self.request.user)

            if self.q:
                qs = qs.filter(title__icontains=self.q)
        return qs
    