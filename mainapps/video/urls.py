from django.urls import path
from . import views

app_name = 'video'

urlpatterns = [
    path('add_video_clip/<int:category_id>/', views.add_video_clip, name='add_video_clip'),
    path('delete_clip/<int:clip_id>/', views.delete_clip, name='delete_clip'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/', views.category_view, name='category_view'),
    path('upload_video_folder/', views.upload_video_folder, name='upload_video_folder'),
    path('add_video_clips/<int:textfile_id>/', views.add_video_clips, name='add_video_clips'),
]
