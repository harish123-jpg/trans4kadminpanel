from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('channels/', views.channel_list, name='channel_list'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('stream/add/', views.add_stream, name='add_stream'),
    path('stream/play/<int:id>/', views.play_stream, name='play_stream'),
    path('stream/stop/<int:id>/', views.stop_stream, name='stop_stream'),
    path('stream/delete/<int:id>/', views.delete_stream, name='delete_stream'),
    path('get_stream_status/', views.get_stream_status_view, name='get_stream_status'),
    path('stream/edit/<int:pk>/', views.edit_stream, name='edit_stream'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
    #path('stream/view/<int:id>/', views.view_channel, name='view_channel'),
    path("test/", views.fast_view),
    path("bandwidth-data/", views.get_bandwidth_data, name="bandwidth_data"),

]
