from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import *
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')

@admin.register(Lavochki)
class LavochkiAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_added')
    change_form_template = 'clientside/admin/change_form.html'

    def get_image(self, obj):
        photo_obj = PhotoLav.objects.filter(lav_id=obj.id)
        return photo_obj

    def response_change(self, request, obj):
        if "send-email" in request.POST:

            current_site = get_current_site(request)

            context = {
                'user': obj.user.username,
                'domain': current_site.domain,
                'protocol': request.scheme,
                'lavid': obj.id,
                'message': request.POST.get("message"),
            }
            message = render_to_string(
                'clientside/admin/send_for_edit.html',
                context=context,
            )
            email = EmailMessage(
                'Редактирование лавочки',
                message,
                to=[obj.user.email],
            )
            email.content_subtype = "html"
            email.send()

            self.message_user(request, "Сообщение отправлено")
            return HttpResponseRedirect(request.path_info)    
        return super().response_change(request, obj)

@admin.register(PhotoLav)
class PhotoLavAdmin(admin.ModelAdmin):
    list_display = ('id', 'lav_id')
    readonly_fields = ('get_image', )

    def get_image(self, obj):
        return mark_safe('<img src="{thumb}" width="750" style="max-width: 100%; height: auto;"/>'.format(
            thumb=obj.image_path.url,
        ))

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'lavochka_id')

@admin.register(RatingStar)
class RatingStarAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')