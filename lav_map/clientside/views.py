from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, get_user_model
from .utils import send_email_for_verify
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.contrib.auth.views import LoginView
from .forms import AuthenticationForm, UserCreationForm, AddLavochkaForm, AddProfileForm, AddMarksForm, AddPhotoForm
from .models import Marks, PhotoLav, Lavochki
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Avg
from django.contrib import messages


# Create your views here.
User = get_user_model()

def pg_index(request):
    return render(request, "pages/index.html")

def pg_lav_points(request):
    data = {
        'objs' : Lavochki.objects.filter(is_valid=True)
    }
    return render(request, "pages/lav_points.html", data)


class AddForm(View):

    template_name = 'pages/add_form.html'
    redirect_authenticated_user = False
    redirect_post = '/add_form/'

    def get(self, request):
        context = {
            'form_lav': AddLavochkaForm(),
            'form_mark': AddMarksForm(),
            'form_photo': AddPhotoForm()
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        lav_form = AddLavochkaForm(request.POST)
        mark_form = AddMarksForm(request.POST)
        photo_form = AddPhotoForm(request.POST, request.FILES)
        user_profile = User.objects.get(pk=request.user.id)
        files = request.FILES.getlist('image_path')
        
        for name, value in kwargs.items():
            lav_obj = Lavochki.objects.get(id=value)
            lav_obj.is_edit = False
            lav_obj.save()
            mark_obj = Marks.objects.get(user_id =user_profile, lavochka_id = lav_obj)
            lav_form = AddLavochkaForm(request.POST, instance=lav_obj)
            mark_form = AddMarksForm(request.POST, instance=mark_obj)
            PhotoLav.objects.filter(lav_id=lav_obj).delete()

        if lav_form.is_valid() and mark_form.is_valid() and photo_form.is_valid() and (len(files) <= 6):
            lav_post = lav_form.save(commit=False)
            lav_post.user = user_profile
            lav_post.save()

            mark_post = mark_form.save(commit=False)
            mark_post.user_id = user_profile 
            mark_post.lavochka_id = lav_post
            mark_post.save()

            for file in files:
                photo_post = PhotoLav(
                    lav_id = lav_post,
                    image_path = file
                )
                photo_post.save()

            context = {
                'form_lav': AddLavochkaForm(),
                'form_mark': AddMarksForm(),
                'form_photo': AddPhotoForm()
            }
            messages.success(request, 'Лавочка успешно отправлена на проверку модератером.')
            return HttpResponseRedirect(self.redirect_post)
        else:
            context = {
                'form_lav': lav_form,
                'form_mark': mark_form,
                'form_photo': photo_form
            }
            messages.error(request, 'Ошибка добавление лавочки проверте форму.')
            return render(request, self.template_name, context)
    
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and (self.request.user.is_authenticated == False):
            redirect_to = "/login/"
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs) 
    

class MyLoginView(LoginView):
    form_class = AuthenticationForm


class Signup(View):

    template_name = 'registration/signup.html'
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = "/lav_points/"
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            send_email_for_verify(request, user)
            return redirect('confirm_email')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

class EmailVerify(View):
    
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('/')
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

def pg_api_points(request):
    data = {
        "type": "FeatureCollection",
        "features": []
    }

    lavochki_obj_list = Lavochki.objects.filter(is_valid=True)
    
    for lavochka in lavochki_obj_list:

        rating = Marks.objects.filter(lavochka_id=lavochka.id).aggregate(Avg('rating'))
        photo_obj_list = PhotoLav.objects.filter(lav_id=lavochka.id).first()
        lavochka = {
            "type": "Feature",
            "id": lavochka.id,
            "geometry": {
                "type": "Point", 
                "coordinates": [lavochka.x, lavochka.y]
            }, 
            "properties": {
                "balloonContent": {'Спинка':lavochka.is_spinka, 'Тень': lavochka.is_ten, 'Падик': lavochka.is_padik},
                "balloonContentHeader": render_to_string('el/map_balloon/head.html', {'id':lavochka.id}), 
                "balloonContentBody": render_to_string('el/map_balloon/body.html', {
                    'id':lavochka.id,
                    'is_spinka':lavochka.is_spinka,
                    'is_ten':lavochka.is_ten,
                    'is_padik':lavochka.is_padik,
                    'photo_lav':photo_obj_list.image_path.url,
                    'rating':rating['rating__avg'],
                }), 
                "balloonContentFooter": render_to_string('el/map_balloon/footer.html', {'id':lavochka.id}), 
                "clusterCaption": render_to_string('el/map_balloon/caption.html', {'id':lavochka.id}), 
                "hintContent": render_to_string('el/map_balloon/hint.html', {'id':lavochka.id}),
            }
        }

        data["features"].append(lavochka)

    return JsonResponse(data)


def pg_profile(request):

    if request.user.is_authenticated:
        add_form = AddProfileForm()
        if request.method == 'POST':
            instance = User.objects.get(pk=request.user.id)
            add_form = AddProfileForm(request.POST, request.FILES, instance=instance)
            if add_form.is_valid():
                new_post = add_form.save(commit=False)
                new_post.save()
                return redirect('profile')
            else:
                return render(request, "pages/profile.html", {"form": add_form})  
        else:
            instance = User.objects.filter(pk=request.user.id).values_list('name')
            sum_lav = Lavochki.objects.filter(user=request.user.id, is_valid=True).count()
            add_form = AddProfileForm(initial={'name': instance[0][0]})
            return render(request, "pages/profile.html", {"form": add_form, "sum_lav": sum_lav})     
    else:
        return redirect('login/')


def pg_lav_page(request, lav_id):
    lav_obj = Lavochki.objects.get(id=lav_id)
    if lav_obj.is_valid:
        photo_obj = PhotoLav.objects.filter(lav_id=lav_id)
        rating = Marks.objects.filter(lavochka_id=lav_id).aggregate(Avg('rating'))['rating__avg']
        try:
            my_rating = Marks.objects.get(lavochka_id=lav_id, user_id=request.user.id).rating
        except Marks.DoesNotExist:
            my_rating = 0

        add_form = AddMarksForm()
        return render(request, "pages/lav_page.html", {"lav_obj": lav_obj, "photo_obj": photo_obj, "form": add_form, "rating": rating, "my_rating": my_rating})
    else:
        return redirect('lav_points')

       
def pg_add_rating(request):
    if request.method == 'POST':
        add_form = AddMarksForm(request.POST)
        if add_form.is_valid():
            Marks.objects.update_or_create(
                user_id = User.objects.get(pk=request.user.id),
                lavochka_id = Lavochki.objects.get(id = request.POST.get("lav_id")),
                defaults = {'rating_id': int(request.POST.get("rating"))}
            )
            lav_obj = Lavochki.objects.get(id=request.POST.get("lav_id"))
            rating = Marks.objects.filter(lavochka_id=request.POST.get("lav_id")).aggregate(Avg('rating'))['rating__avg']
            my_rating = Marks.objects.get(lavochka_id=request.POST.get("lav_id"), user_id=request.user.id).rating
            add_form = AddMarksForm()
            return render(request, "pages/raiting_form.html", {"lav_obj": lav_obj, "form": add_form, "rating": rating, "my_rating": my_rating})   
        else:
            return HttpResponse(status=400)
        
class EditForm(AddForm):

    template_name = 'pages/edit_form.html'
    redirect_authenticated_user = False
    redirect_post = '/lav_points/'

    def get(self, request, lav_id):
        lav_obj = Lavochki.objects.get(id=lav_id)
        if (lav_obj.user == request.user) and lav_obj.is_edit:
            lav_form = AddLavochkaForm(instance=lav_obj)
            context = {
                'form_lav': lav_form,
                'form_mark': AddMarksForm(),
                'form_photo': AddPhotoForm()
            }
            return render(request, self.template_name, context)
        else:
            return redirect('lav_points')

    

        






