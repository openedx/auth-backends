""" Authentication views. """

from django.contrib.auth import logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import RedirectView


class LogoutRedirectBaseView(RedirectView):
    """ Base logout view for projects with single sign out/logout.

    This is a base view. You MUST override `url` attribute or `get_redirect_url` method to make this view useful. See
    the documentation for `RedirectView` for more info:
    https://docs.djangoproject.com/en/1.9/ref/class-based-views/base/#redirectview.

    If the `no_redirect` querystring argument is set, the view will not redirect. An empty 200 response will be
    returned instead.

    This view is intended to be used with Django projects that need to implement single sign out/logout. After their
    session is destroyed, the user will be redirected to the specified logout page on the authorization server/identity
    provider. Additionally, no X-Frame-Options header is set, allowing this page to be loaded in an iframe on the
    authorization server's logout page. This allows signout to be triggered by the authorization server.
    """
    permanent = False

    @method_decorator(xframe_options_exempt)
    def dispatch(self, request, *args, **kwargs):
        logout(request)

        if request.GET.get('no_redirect'):
            return HttpResponse()

        return super(LogoutRedirectBaseView, self).dispatch(request, *args, **kwargs)
