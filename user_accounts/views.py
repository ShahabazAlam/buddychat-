from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, RedirectView
from user_accounts.forms import UserCreationForm,UserLoginForm,UsernameField,UserRegistrationForm
from user_accounts.models import User
from Profile.models import user_Detail

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'login_register/register.html'
    success_url = '/user_accounts/login/'

    extra_context = {
        'title': 'Register'
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(self.request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        if User.objects.filter(email=request.POST['email']).exists():
            messages.warning(request, 'This email is already taken')
            return redirect('/user_accounts/register')

        user_form = UserRegistrationForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get("password1")
            email = user_form.cleaned_data.get("email")
            dob = request.POST.get("dob")
            user.username = email
            user.set_password(password)
            user.save()
            user_Detail.objects.create(user=user,dob=dob)
            messages.success(request, 'Created Successfully! Please Login ')
            return redirect('/user_accounts/login/')
        else:
            return render(request, 'login_register/register.html',{'form':user_form})


class LoginView(FormView):
    success_url = '/'
    form_class = UserLoginForm
    template_name = 'login_register/login.html'

    extra_context = {
        'title': 'Login'
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(self.request, *args, **kwargs)

    def get_form_class(self):
        return self.form_class

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = reverse_lazy('user_accounts:login')

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return super(LogoutView, self).get(request, *args, **kwargs)
