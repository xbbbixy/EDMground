from django.shortcuts import redirect
from functools import wraps


def frontend_login_required(view_func):
    """
    只允许「前端普通用户」访问：
    - 未登录 → 去前端登录页
    - staff/admin → 去 Django Admin
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        if request.user.is_staff:
            return redirect('users:login')

        return view_func(request, *args, **kwargs)

    return _wrapped
