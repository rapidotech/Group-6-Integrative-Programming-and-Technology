from django.contrib import admin
from django.urls import path, include
from posts.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls')),
    path('login/', LoginView.as_view(), name='login'),
]