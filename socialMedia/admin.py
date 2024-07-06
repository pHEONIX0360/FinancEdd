from django.contrib import admin
from socialMedia.models import Follow, Message, Post, Reaction


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'created_at', 'likes_count', 'dislikes_count', 'reports_count')
    search_fields = ('user__username', 'description')
    list_filter = ('created_at',)

class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction', 'created_at')
    search_fields = ('user__username', 'post__description', 'reaction')
    list_filter = ('reaction', 'created_at')

admin.site.register(Post, PostAdmin)
admin.site.register(Reaction, ReactionAdmin)
admin.site.register(Follow)
admin.site.register(Message)