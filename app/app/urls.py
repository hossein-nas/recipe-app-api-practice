from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/user/', include('user.urls')),
                  path('api/recipe/', include('recipe.urls'))
              ] + static(settings.MEDIA_URL, dcoument_root=settings.MEDIA_ROOT)
