from catalog import settings

def media(request):
    """
    Adds media-related context variables to the context.
    """
    return {'CATALOG_MEDIA_URL': settings.CATALOG_MEDIA_URL}
