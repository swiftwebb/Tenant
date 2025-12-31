


def tenant(request):
    # request.tenant is set by django-tenants
    return {'tenant': getattr(request, 'tenant', None)}
