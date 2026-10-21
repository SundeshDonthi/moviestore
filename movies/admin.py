from django.contrib import admin

# Register your models here.
from .models import Movie, Review, Report, Rating
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "review", "reporter", "created_at", "resolved"]
    list_filter = ["resolved", "created_at"]
    search_fields = ["reporter__username", "review__comment"]

    actions = ["mark_resolved", "restore_review"]

    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True)
        self.message_user(request, "Selected reports have been marked as resolved.")
    mark_resolved.short_description = "Mark selected reports as resolved"

    def restore_review(self, request, queryset):
        restored = 0
        for report in queryset:
            review = report.review
            if review.is_removed:
                review.is_removed = False
                review.save()
                restored += 1
        self.message_user(request, f"{restored} reviews have been restored.")
    restore_review.short_description = "Restore reviews for selected reports"

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Report, ReportAdmin)
admin.site.register(Rating)
