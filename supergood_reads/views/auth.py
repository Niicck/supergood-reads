from typing import Any, Literal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest, HttpResponseRedirect

from supergood_reads.models import BaseMediaItem, Review


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
    obj: BaseMediaItem | Review,
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
        if obj.validated and not user.has_perm("supergood_reads.change_review"):
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
            obj.validated
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
        """Check if user is allowed to change MediaItem instance."""
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return user.has_perm("supergood_reads.delete_review") or has_owner_permission(
            user, obj
        )


class CreateMediaItemPermissionMixin(BasePermissionMixin):
    request: HttpRequest

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        # TODO: check permissions on MediaItem
        if not request.user.is_authenticated:
            self.send_demo_notification()
        return super().get(request, *args, **kwargs)  # type: ignore

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Only allow authenticated users to create new Reviews."""
        # TODO: check permissions on MediaItem
        if not request.user.is_authenticated:
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore


class UpdateMediaItemPermissionMixin(BasePermissionMixin):
    request: HttpRequest

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_get_permission():
            return self.handle_unauthorized()

        if not self.has_post_permission():
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
          - The review is a validated demo Media Item
          - The user owns the Media Item
        """
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return obj.validated or has_owner_permission(user, obj)

    def has_post_permission(self) -> bool:
        """
        A user can only update a MediaItem if one of these conditions is met:
          - The user has global "change_media_item" permission
          - The user owns the Media Item
        """
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return has_owner_permission(user, obj) or user.has_perm(
            "supergood_reads.change_book"
        )


class DeleteMediaPermissionMixin(BasePermissionMixin):
    request: HttpRequest

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not self.has_post_permission():
            return self.handle_unauthorized()
        return super().post(request, *args, **kwargs)  # type: ignore

    def has_post_permission(self) -> bool:
        """Check if user is allowed to change MediaItem instance."""
        user = self.request.user
        obj = self.get_object()  # type: ignore
        return has_owner_permission(user, obj) or user.has_perm(
            "supergood_reads.delete_book"
        )
