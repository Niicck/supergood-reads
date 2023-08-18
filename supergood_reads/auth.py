from typing import Any, Literal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest, HttpResponseRedirect

from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.reviews.models import Review


def has_perm_dynamic(
    user: User | AnonymousUser,
    obj: Model,
    perm: Literal["view", "add", "change", "delete"],
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
    user: User | AnonymousUser,
    obj: AbstractMediaType | Review,
) -> bool:
    return user.is_authenticated and obj.owner == user


class BasePermissionMixin:
    request: HttpRequest

    def handle_unauthorized(self) -> HttpResponseRedirect:
        if not self.request.user.is_authenticated:
            return redirect_to_login(settings.LOGIN_URL)
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
    request: HttpRequest

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not request.user.has_perm("supergood_reads.add_review"):
            self.send_demo_notification()
        return super().get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Only allow authenticated users to create new Reviews."""
        if not request.user.has_perm("supergood_reads.add_review"):
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore


class UpdateReviewPermissionMixin(BasePermissionMixin):
    request: HttpRequest

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        user = request.user
        if not self.has_get_permission():
            return self.handle_unauthorized()

        obj = self.get_object()  # type: ignore
        if obj.demo and not user.has_perm("supergood_reads.change_review"):
            self.send_demo_notification()

        return super().get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_post_permission():
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore

    def has_get_permission(self) -> bool:
        """
        A user can only view the update page for a review only if one of these
        conditions is met:
          - The review is a demo review
          - The user has a global "view_review" permission
          - The user owns the Review
        """
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return (
            obj.demo
            or user.has_perm("supergood_reads.view_review")
            or has_owner_permission(user, obj)
        )

    def has_post_permission(self) -> bool:
        """
        A user can only update a review if one of these conditions is met:
          - The user has global "change_review" permission
          - The user owns the Review
        """
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return user.has_perm("supergood_reads.change_review") or has_owner_permission(
            user, obj
        )


class DeleteReviewPermissionMixin(BasePermissionMixin):
    request: HttpRequest

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_post_permission():
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore

    def has_post_permission(self) -> bool:
        """Check if user is allowed to change MediaType instance."""
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return user.has_perm("supergood_reads.delete_review") or has_owner_permission(
            user, obj
        )


class BaseJsonPermissionMixin(BasePermissionMixin):
    pass


class UpdateMediaPermissionMixin(BaseJsonPermissionMixin):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Check if user is allowed to change MediaType instance."""
        user = request.user
        obj = self.get_object()  # type: ignore
        if not obj.can_user_change(user):
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore


class DeleteMediaPermissionMixin(BaseJsonPermissionMixin):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Check if user is allowed to change MediaType instance."""
        user = request.user
        obj = self.get_object()  # type: ignore
        if not obj.can_user_delete(user):
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore
