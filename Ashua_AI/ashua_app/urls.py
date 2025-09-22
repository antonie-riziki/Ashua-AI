from django.urls import path, include
from . import views
# from django.contrib.auth.views import LoginView,LogoutView
from django.conf import settings
from django.conf.urls.static import static


from django.http import JsonResponse

def chrome_devtools_placeholder(request):
    return JsonResponse({}, safe=False)


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("process-audio/", views.process_audio, name="process_audio"),
    path("process-text/", views.process_text, name="process_text"),
    path(".well-known/appspecific/com.chrome.devtools.json", chrome_devtools_placeholder),

]