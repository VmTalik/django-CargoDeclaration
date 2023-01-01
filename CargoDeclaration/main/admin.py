from django.contrib import admin
from .models import AdvUser
from .utilities import send_activation_notification
import datetime
from .models import Cargo, DeclarationLog, CargoReceiver, Consignor, Status, Orientation, DeclarationLogArchive


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Электронные письма с требованиями отправлены')


send_activation_notifications.short_description = 'Отправление писем с требованиями об активации'


class NonactivatedFilter(admin.SimpleListFilter):
    """Фильтрация пользователей, выполнивших
    активацию, не выполнивших ее в течение трех дней и недели"""
    title = 'Активация пройдена?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли уже более 3 дней'),
            ('week', 'Не прошли уже более недели'),

        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'firstname', 'lastname')
    list_filter = (NonactivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'), 'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)


admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Cargo)
admin.site.register(DeclarationLog)
admin.site.register(CargoReceiver)
admin.site.register(Consignor)
admin.site.register(Status)
admin.site.register(Orientation)
admin.site.register(DeclarationLogArchive)
