from django.utils.text import slugify
from unidecode import unidecode


def generate_unique_slug(
        model_instance,
        slugable_field_name='title',
        slug_field_name='slug'
):
    """
    Generates unique slug for any item in Django model.
    """
    slugable_value = getattr(model_instance, slugable_field_name)
    base_slug = slugify(unidecode(slugable_value))
    if not base_slug:
        base_slug = "item"
    slug = base_slug
    counter = 2
    model_class = model_instance.__class__
    while model_class.objects.filter(**{slug_field_name: slug}).exclude(pk=model_instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
