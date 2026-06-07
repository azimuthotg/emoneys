"""
URL configuration for edoc_system project.
File-based authentication system URLs.
"""
import time

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.db import connection
from django.http import JsonResponse
from accounts.views import receipt_check_public_view


# Health endpoint สำหรับ NMS Agent monitoring — เช็ก DB ด้วย SELECT 1 (public)
def health(request):
    t0 = time.monotonic()
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {e}'
    db_ms = round((time.monotonic() - t0) * 1000)
    status = 'ok' if db_status == 'ok' else 'degraded'
    return JsonResponse(
        {'status': status, 'db': db_status, 'db_ms': db_ms},
        status=200 if status == 'ok' else 503,
    )


urlpatterns = [
    path('health/', health, name='nms_health'),  # NMS monitoring
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),  # Keep root URLs for backwards compatibility

    # Summernote WYSIWYG Editor
    path('summernote/', include('django_summernote.urls')),

    # QR Code Public Check URLs (สั้นๆ)
    # URL ใหม่: รวมรหัสหน่วยงาน
    path('check/<str:dept_code>/<str:date_part>/<str:number_part>/', receipt_check_public_view, name='receipt_check_public_direct_with_dept'),
    # URL เก่า: backward compatibility
    path('check/<str:date_part>/<str:number_part>/', receipt_check_public_view, name='receipt_check_public_direct'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)