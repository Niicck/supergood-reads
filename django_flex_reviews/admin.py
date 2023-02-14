from django.contrib import admin


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("media", "view_completed_at")
    list_select_related = ("media",)

    @admin.display
    def view_completed_at(self, obj):
        return obj.completed_at
