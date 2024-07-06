# urls.py
from django.urls import path,re_path
from socialMedia import views as socialViews
from adminapp import views as adminappView
from .swagger import schema_view

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('socialmedia/post/list', socialViews.listPosts, name='listPosts'),
    path('socialmedia/post', socialViews.savePost, name='savePost'),
    path('socialmedia/post/reactions', socialViews.listReactions, name='listReactions'),
    path('socialmedia/post/reaction', socialViews.reactToPost, name='reactToPost'),
    path('socialmedia/post/comment', socialViews.postComment, name='postComment'),
    path('socialmedia/post/comments/<int:post_id>', socialViews.getComments, name='getComments'),
    path('socialmedia/users/list', socialViews.listUsers, name='listUsers'),
    path('socialmedia/user/follow', socialViews.followUser, name='followUser'),
    path('socialmedia/user/followers/list', socialViews.listFollowingUsers, name='listFollowingUsers'),
    path('socialmedia/user/unfollowers/list', socialViews.listUnfollowedUsers, name='listUnfollowedUsers'),
    path('socialmedia/user/info', socialViews.userDetails, name='userDetails'),
    path('send_message/', socialViews.send_message, name='send_message'),
    path('get_messages/<int:user_id>/<int:recipient_id>/', socialViews.get_messages, name='get_messages'),
    path('students/list', socialViews.getAllStudents, name='getAllStudents'),
    path('query/', adminappView.query_view, name='query_view'),

]