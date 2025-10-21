from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import View
from django.http import FileResponse, Http404
from django.contrib.staticfiles import finders

urlpatterns = [
    path('admin/', admin.site.urls),
    # serve service worker at site root so it has scope over the whole site
    path('service-worker.js', lambda request: FileResponse(open(finders.find('service-worker.js'), 'rb'), content_type='application/javascript')),
    path('', include('core.urls')),
    # Mount blog app at /blog/
    path('blog/', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
