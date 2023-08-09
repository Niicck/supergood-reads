from typing import Any, Literal

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest, HttpResponseRedirect

from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.reviews.models import Review


def has_perm_dynamic(
    user: User, obj: Model, perm: Literal["view", "add", "change", "delete"]
) -> bool:
    """
    Test user permissions for any object and any base permission.

    Example:
        has_perm_dynamic(user, book, "view")
        Returns:
        user.has_perm("supergood_reads.view_book", book)
    """
    perm_string = f"{obj._meta.app_label}.{perm}_{obj._meta.model_name}"
    return user.has_perm(perm_string, obj)


def has_owner_permission(
    user: User,
    obj: AbstractMediaType | Review,
) -> bool:
    return user.is_authenticated and obj.owner == user


class BasePermissionMixin:
    def handle_unauthorized(self, request: HttpRequest) -> HttpResponseRedirect:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        else:
            raise PermissionDenied()

    def send_demo_notification(self) -> None:
        messages.info(
            self.request,
            (
                "This is just a demo form, you can't submit it. If you want to "
                "create or update your own reviews, please sign in!"
            ),
        )


class CreateReviewPermissionMixin(BasePermissionMixin):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        self.send_demo_notification()
        return super().get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Only allow authenticated users to create new Reviews."""
        user = request.user
        if not user.has_perm("supergood_reads.add_review"):
            return self.handle_unauthorized(request)
        return super().post(request, *args, **kwargs)  # type: ignore


class UpdateReviewPermissionMixin(BasePermissionMixin):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_get_permission(request):
            return self.handle_unauthorized(request)

        obj = self.get_object()  # type: ignore
        if obj.is_demo():
            self.send_demo_notification()

        return super().get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_post_permission(request):
            return self.handle_unauthorized(request)
        return super().post(request, *args, **kwargs)  # type: ignore

    def has_get_permission(self, request: HttpRequest) -> bool:
        """
        A user can only view the update page for a review only if one of these
        conditions is met:
          - The review is a demo review
          - The user has a global "view_review" permission and is_staff
          - The user owns the Review
        """
        user = request.user
        obj = self.get_object()  # type: ignore
        has_staff_perm = user.has_perm("supergood_reads.view_review") and user.is_staff
        return obj.is_demo() or has_staff_perm or has_owner_permission(user, obj)

    def has_post_permission(self, request: HttpRequest) -> bool:
        """
        A user can only update a review if one of these conditions is met:
          - The user has global "change_review" permission and is_staff
          - The user owns the Review
        """
        user = request.user
        obj = self.get_object()  # type: ignore
        has_staff_perm = (
            user.has_perm("supergood_reads.change_review") and user.is_staff
        )
        return has_staff_perm or has_owner_permission(user, obj)


class DeleteReviewPermissionMixin(BasePermissionMixin):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_post_permission(request):
            return self.handle_unauthorized(request)
        return super().post(request, *args, **kwargs)  # type: ignore

    def has_post_permission(self, request) -> bool:
        """Check if user is allowed to change MediaType instance."""
        user = request.user
        obj = self.get_object()  # type: ignore
        has_staff_perm = (
            user.has_perm("supergood_reads.delete_review") and user.is_staff
        )
        return has_staff_perm or has_owner_permission(user, obj)


class BaseJsonPermissionMixin(BasePermissionMixin):
    pass


class UpdateMediaPermissionMixin(BaseJsonPermissionMixin):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Check if user is allowed to change MediaType instance."""
        user = request.user
        obj = self.get_object()  # type: ignore
        if not obj.can_user_change(user):
            return self.handle_unauthorized(request)
        return super().post(request, *args, **kwargs)  # type: ignore


class DeleteMediaPermissionMixin(BaseJsonPermissionMixin):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Check if user is allowed to change MediaType instance."""
        user = request.user
        obj = self.get_object()  # type: ignore
        if not obj.can_user_delete(user):
            return self.handle_unauthorized(request)
        return super().post(request, *args, **kwargs)  # type: ignore
