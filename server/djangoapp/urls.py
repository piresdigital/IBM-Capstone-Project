from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL

    # path for about view
    path('about-us', view=views.about_us, name='about-us'),

    # path for contact us view
    path('contact-us', view=views.contact_us, name='contact-us'),

    # path for registration
    path('signup', view=views.registration_request, name='signup'),

    # path for login
    path('login', view=views.login_request, name="login"),

    # path for logout
    path('logout', view=views.logout_request, name='logout'),

    # path for djangoapp home
    path('', view=views.get_dealerships, name='index'),

    # path for dealer reviews view
    path('dealer/<int:dealer_id>/',
         view=views.get_dealer_details, name='dealer_details'),

    # path for add a review view
    path('dealer/<int:dealer_id>/add_review',
         view=views.add_review, name='add_review'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
