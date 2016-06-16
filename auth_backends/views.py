""" Authentication views. """
import logging

from django.contrib.auth import logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import RedirectView
from social.apps.django_app.utils import load_strategy, load_backend

logger = logging.getLogger(__name__)


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
    user = None

    @method_decorator(xframe_options_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Keep track of the user so that child classes have access to it after logging out.
        self.user = request.user
        logout(request)

        if request.GET.get('no_redirect'):
            return HttpResponse()

        return super(LogoutRedirectBaseView, self).dispatch(request, *args, **kwargs)


class EdxOpenIdConnectLoginView(RedirectView):
    """ Login view for projects utilizing edX OpenID Connect for single sign-on.

    Usage of this view requires `python-social-auth` to be installed and configured in `urls.py`.
    """
    permanent = False
    query_string = True
    url = reverse_lazy('social:begin', args=['edx-oidc'])


class EdxOpenIdConnectLogoutView(LogoutRedirectBaseView):
    """ Logout view for projects utilizing edX OpenID Connect for single sign-on. """

    def get_redirect_url(self, *args, **kwargs):
        strategy = load_strategy(self.request)
        backend = load_backend(strategy, 'edx-oidc', None)
        return backend.logout_url
