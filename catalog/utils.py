"""
Utility functions for the video game catalog application.

Contains helper functions for dynamic validations and generating
unique URL slugs for model instances.
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode


DEFAULT_SLUG_PLACEHOLDER = "item"
SLUG_COUNTER_START = 2


def current_year():
    """Return the current year as an integer.

    Used as a dynamic upper bound for year validation in models.

    Returns:
        int: The current calendar year.
    """
    return timezone.now().year


def generate_unique_slug(
        model_instance: models.Model,
        slugable_field_name: str = 'title',
        slug_field_name: str = 'slug'
) -> str:
    """
    Generates a unique slug for any item in a Django model.

    Converts the value of the specified field into a URL-friendly string
    using unidecode and slugify. If the resulting slug already exists in
    the database for the given model, it appends an incremental counter
    (e.g., '-2', '-3') until a unique slug is found.

    Args:
        model_instance (models.Model): The Django model instance for which
            the slug is being generated.
        slugable_field_name (str, optional): The name of the attribute on the
            model instance to base the slug on. Defaults to 'title'.
        slug_field_name (str, optional): The name of the field in the database
            to check for existing slugs. Defaults to 'slug'.

    Returns:
        str: A unique URL-friendly slug string.
    """
    slugable_value = getattr(model_instance, slugable_field_name)
    base_slug = slugify(unidecode(str(slugable_value)))
    if not base_slug:
        base_slug = DEFAULT_SLUG_PLACEHOLDER

    model_class = model_instance.__class__
    existing_slugs = set(
        model_class.objects
        .filter(**{f'{slug_field_name}__startswith': base_slug})
        .exclude(pk=model_instance.pk)
        .values_list(slug_field_name, flat=True)
    )

    if base_slug not in existing_slugs:
        return base_slug

    counter = SLUG_COUNTER_START
    slug = f"{base_slug}-{counter}"
    while slug in existing_slugs:
        counter += 1
        slug = f"{base_slug}-{counter}"

    return slug
