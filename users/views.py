from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import auth, messages
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect

from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView
from django.views import View

from app.settings import EMAIL_HOST_USER, APP_NAME, MEDIA_ROOT
from main.services import create_random_image
from users.models import User
from users.forms import UserLoginForm, UserRegisterForm, UserProfileForm, ResetTokenForm, ResetPasswordForm, SetNewPasswordForm
from users.services import generate_token
from users.tasks import send_email_to, clear_activation_key


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('user:reset_wait')

    def form_valid(self, form: UserRegisterForm):

        email = form.cleaned_data['email']
        user, created = User.objects.get_or_create(email=email)

        if created or user.is_active == False:
            activation_code = generate_token()
            activation_url = self.request.build_absolute_uri(
                reverse_lazy('user:register_confirm', kwargs={'token': activation_code}))

            send_mail(
                subject=f'Код активації акаунта ({APP_NAME})',
                message=f'({APP_NAME}) Код активації акаунта: {activation_code}',
                html_message=f"""
                    <h2>Код активації акаунта ({APP_NAME})</h2>
                    <p>Код: <b>{activation_code}</b></p>
                    <p>або перейдіть за посиланням <a href="{activation_url}">{activation_url}</a></p>""",
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False)

            user.is_active = False
            user.activation_key = activation_code
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # clear_activation_key.apply_async((user.pk,), countdown=300)

        messages.success(
            self.request, 'На ваш email надіслано лист з посиланням для підтвердження акаунта')
        return super().form_valid(form)

    def form_invalid(self, form: UserRegisterForm):
        return self.render_to_response(self.get_context_data(form=form))


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        next_url = self.request.GET.get(
            'next') or self.request.POST.get('next')
        if next_url:
            return next_url

        return reverse('user:profile')


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request: HttpRequest):
        form = UserProfileForm(instance=request.user)

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserProfileForm(
            data=request.POST, instance=request.user, files=request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Дані користувача успішно змінено')

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


class UserLogoutView(View):

    def get(self, request: HttpRequest):
        next_page = request.GET.get('next', 'main:index')

        if request.user.is_authenticated:
            messages.success(request, 'Ви вийшли з акаунта')
            auth.logout(request)

        return redirect(next_page)


class ResetWaitView(FormView):
    template_name = 'users/reset_wait.html'
    form_class = ResetTokenForm
    token: str

    def form_valid(self, form):
        self.token = form.cleaned_data['token']
        self.success_url = reverse_lazy(
            'user:register_confirm', kwargs={'token': self.token})
        return super().form_valid(form)


class UserRegisterConfirmView(View):
    def get(self, request: HttpRequest, token):
        try:
            user = User.objects.get(activation_key=token)

        except User.DoesNotExist:
            messages.error(
                request, 'Неправильний код активації або код застарів')
            return redirect('user:reset_wait')

        except Exception:
            messages.error(request, 'Помилка активації')
            return redirect('user:reset_wait')

        image_path = f'images/users/avatar/{user.username}.png'
        create_random_image(MEDIA_ROOT / image_path)

        user.is_active = True
        user.activation_key = None
        user.avatar = image_path
        user.save(update_fields=['is_active', 'activation_key', 'avatar'])

        auth.login(request, user)
        messages.success(request, 'Ви успішно зареєструвались')

        return redirect('user:profile')


class PasswordResetView(FormView):
    template_name = 'users/password_reset.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('user:login')

    def form_valid(self, form: ResetPasswordForm):
        email = form.cleaned_data['email']
        user: User = User.objects.filter(email=email).first()

        if user:
            token = generate_token()
            user.activation_key = token
            user.save()
            reset_url = self.request.build_absolute_uri(
                reverse_lazy('user:password_reset_confirm', kwargs={'token': token}))

            send_mail(
                subject=f'Відновлення паролю на сайті ({APP_NAME})',
                message=f'({APP_NAME}) Щоб відновити пароль перейдіть за посиланням: {reset_url}',
                html_message=f"""
                    <h2>Відновлення паролю на сайті ({APP_NAME})</h2>
                    <p>Щоб відновити пароль перейдіть за посиланням: {reset_url}</p>
                    """,
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False)

            messages.success(
                self.request, 'Перевірте свою електронну пошту для відновлення паролю.')
        else:
            messages.error(
                self.request, 'Користувача з такою електронною поштою не знайдено.')

        return super().form_valid(form)


class UserPasswordResetConfirmView(FormView):
    template_name = 'users/password_reset_confirm.html'
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('user:profile')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        user = self.get_user_by_token(token)

        if user is None:
            messages.error(
                self.request, 'Це посилання для зміни пароля застаріло')
            return redirect('main:index')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form: SetNewPasswordForm):
        token = self.kwargs.get('token')
        user = self.get_user_by_token(token)
        if user:
            user.set_password(form.cleaned_data['password1'])
            user.activation_key = None
            user.save()
            messages.success(
                self.request, 'Пароль успішно змінено. Увійдіть з новим паролем.')
        else:
            messages.error(
                self.request, 'Неправильний токен для зміни пароля.')
        return super().form_valid(form)

    def get_user_by_token(self, token):
        try:
            return User.objects.get(activation_key=token)
        except User.DoesNotExist:
            return None


class UserDetailView(DetailView):

    def get(self, request: HttpRequest, username):
        user = get_object_or_404(User, username=username)
        context = {
            'title': user.description,
            'detail_user': user,
        }
        return render(request, 'users/user_detail.html', context)
