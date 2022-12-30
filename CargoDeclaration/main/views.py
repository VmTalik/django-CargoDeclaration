from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import AdvUser
from .forms import ChangeInfoFormUser
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import CreateView
from .forms import RegisterFormUser
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from .utilities import signer
from django.views.generic.edit import DeleteView
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.shortcuts import redirect
from .forms import DeclarationForm, CargoReceiverForm, ConsignorForm, SummmaryForm
from .models import DeclarationLog, CargoReceiver, Summary, Consignor


class BbLoginView(LoginView):
    template_name = 'main/login.html'


class BbLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


def index(request):
    declrs = DeclarationLog.objects.all()
    print(declrs)
    context = {'declrs': declrs}
    return render(request, 'main/index.html', context)


@login_required
def declrlog(request):
    declrs = DeclarationLog.objects.filter(user_id=request.user.pk)
    context = {'declrs': declrs}
    return render(request, 'main/declrlog.html', context)


def declrarchive(request):
    declrs = DeclarationLog.objects.filter(status=2)
    context = {'declrs': declrs}
    return render(request, 'main/archive.html', context)


@login_required
def summary(request):
    declrs = DeclarationLog.objects.all()
    declrs_summary = Summary.objects.all()
    context = {'declrs': declrs, 'declrs_summary': declrs_summary}
    return render(request, 'main/summary.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    """Функция-контроллер, вывод объявлений текущего пользователя"""
    return render(request, 'main/profile.html')
    # bbs = Bb.objects.filter(author=request.user.pk)
    # context = {'bbs': bbs}
    # return render(request, 'main/profile.html', context)


class ChangeInfoViewUser(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeInfoFormUser
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя успешно изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BbPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Изменение пароля пользователя прошло успешно!'


class RegisterViewUser(CreateView):
    """Класс - контроллер для регистрации пользователя"""
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterFormUser
    success_url = reverse_lazy('main:register_done')


class RegisterViewDone(TemplateView):
    """Класс - контроллер, выводящий сообщение об успешной регистрации"""
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    """Функция конроллер для активации нового пользователя"""
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteViewUser(LoginRequiredMixin, DeleteView):
    """Класс-контроллер, удаляющий текущего пользователя"""
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь успешно удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordViewReset(PasswordResetView):
    """Класс-контроллер. Запрос на сброс пароля"""
    template_name = 'main/reset_password.html'
    subject_template_name = 'email/reset_subject_email.txt'
    email_template_name = 'email/reset_email.txt'
    success_url = reverse_lazy('main:password_reset_done')


class PasswordResetViewDone(PasswordResetDoneView):
    """Класс-котнроллер. Уведомление о том что письмо о сбросе пароля отправлено на почту"""
    template_name = 'main/password_reset_done.html'


class PasswordResetViewConfirm(PasswordResetConfirmView):
    """Класс-контроллер. Сброс старого пароля"""
    template_name = 'main/password_reset_confirm.html'
    success_url = reverse_lazy('main:password_reset_complete')


class PasswordResetViewComplete(PasswordResetCompleteView):
    """Класс-контроллер. Уведомление об успешном сбросе пароля"""
    template_name = 'main/password_confirmed.html'


@login_required
def profile_declaration_add(request):
    """Функция для добавления декларации"""
    if request.method == 'POST':
        form1 = DeclarationForm(request.POST)
        form2 = CargoReceiverForm(request.POST)
        form3 = ConsignorForm(request.POST)

        if all([form2.is_valid(), form3.is_valid()]):
            form1.save(), form2.save(), form3.save()
            messages.add_message(request, messages.SUCCESS, 'Декларация успешно добавлена')
            return redirect('main:profile')

    else:
        form1 = DeclarationForm(initial={'user_id': request.user.pk})
        form2 = CargoReceiverForm(initial={'id': DeclarationLog.pk})
        form3 = ConsignorForm(initial={'id': DeclarationLog.pk})
    context = {'form1': form1, 'form2': form2, 'form3': form3}
    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_declr_change(request, pk):
    """Функция-контроллер для правки декларации"""
    d = get_object_or_404(DeclarationLog, pk=pk)
    if request.method == 'POST':
        form1 = DeclarationForm(request.POST, instance=d)
        form2 = CargoReceiverForm(request.POST)
        form3 = ConsignorForm(request.POST)

        if all([form2.is_valid(), form3.is_valid()]):
            form1.save(), form2.save(), form3.save()
            messages.add_message(request, messages.SUCCESS, 'Декларация успешно добавлена')
            return redirect('main:profile')

    else:
        form1 = DeclarationForm(initial={'user_id': request.user.pk})
        form2 = CargoReceiverForm(initial={'id': DeclarationLog.pk})
        form3 = ConsignorForm(initial={'id': DeclarationLog.pk})
    context = {'form1': form1, 'form2': form2, 'form3': form3}
    return render(request, 'main/profile_declr_change.html', context)


@login_required
def summary_check(request, pk):
    """Функция-контроллер для проверки декларации (проверяет инспектор)"""
    d = get_object_or_404(DeclarationLog, pk=pk)
    declr = DeclarationLog.objects.get(pk=pk)
    receiver = CargoReceiver.objects.get(pk=pk)
    consignor = Consignor.objects.get(pk=pk)
    if request.method == 'POST':
        form4 = SummmaryForm(request.POST)

        if form4.is_valid():
            form4.save()
            messages.add_message(request, messages.SUCCESS, 'Декларация проверена')
            return redirect('main:profile')

    else:
        form4 = SummmaryForm(initial={'id': DeclarationLog.pk})

    context = {'declr': declr, 'receiver': receiver, 'consignor': consignor, 'form4': form4}
    return render(request, 'main/summary_check.html', context)


@login_required
def profile_declr_delete(request, pk):
    """Функция-контроллер для удаления декларации"""
    d = get_object_or_404(DeclarationLog, pk=pk)
    if request.method == 'POST':
        d.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено!')
        return redirect('main:profile')
    else:
        context = {'d': d}
        return render(request, 'main/profile_declr_delete.html', context)
