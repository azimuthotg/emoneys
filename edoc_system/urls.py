"""
URL configuration for edoc_system project.
File-based authentication system URLs.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import receipt_check_public_view

urlpatterns = [
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