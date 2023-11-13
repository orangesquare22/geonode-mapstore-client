from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from django.db.models import signals
from django.core.cache import caches

from geonode_mapstore_client.templatetags.get_search_services import populate_search_service_options


class SearchService(models.Model):
    class Meta:
        verbose_name = _("Search Service")

    def __str__(self):
        return f"{self.display_name} - {self.url}"

    display_name = models.CharField(
        max_length=250, null=False, verbose_name="Display name"
    )
    priority = models.IntegerField(null=False, verbose_name="Priority", default=3)
    url = models.CharField(
        max_length=250,
        null=False,
        verbose_name="Url of the WFS service",
        default="",
    )
    typename = models.CharField(
        max_length=250,
        null=False,
        verbose_name="Typename",
        help_text="Geonode alternate",
    )
    attributes = ArrayField(
        max_length=250,
        null=False,
        base_field=models.CharField(max_length=250, null=False),
        verbose_name="Attributes",
        help_text="Attribute lists, the search is performed in this fields",
    )
    sortby = models.CharField(
        max_length=250,
        null=False,
        verbose_name="Sort By",
        help_text="Sorting attribute, must be a dataset attribute",
    )
    srsName = models.CharField(
        max_length=250, null=False, verbose_name="srsName", default="EPSG:4326"
    )
    maxFeatures = models.IntegerField(
        null=False,
        verbose_name="Max Features",
        default=20,
        help_text="Max number of feature returned by the search",
    )

@receiver(signals.post_save, sender=SearchService)
def post_save_search_service(instance, sender, created, **kwargs):
    # reset subsite object cache
    services_cache = caches["search_services"]
    services = services_cache.get("search_services")
    if services:
        services_cache.delete("search_services")

    services_cache.set("search_services", populate_search_service_options(), 300)
