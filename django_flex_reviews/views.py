from django.views.generic.edit import FormView

from django_flex_reviews.reviews.forms import ReviewForm


class ReviewFormView(FormView[ReviewForm]):
    template_name = "review_form.html"
