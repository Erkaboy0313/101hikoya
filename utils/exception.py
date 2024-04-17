from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

class BaseAPIException(APIException):
    status_code = 400
    default_detail = _('fail_perform')
    default_code = 'error'