from django.urls import path
from .views import publish_message

urlpatterns = [
   # path('/', admin.site.urls),
    path('', publish_message, name='publish'),
]
