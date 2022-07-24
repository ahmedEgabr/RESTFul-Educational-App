from dal import autocomplete
from .models import Reference
from alteby.permissions import StafUserRequiredMixin

class ReferenceAutocomplete(StafUserRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        reference_category = self.forwarded.get('reference_category', None)
        qs = None
        if reference_category:
            qs = Reference.objects.filter(categories__in=[reference_category])
        return qs
