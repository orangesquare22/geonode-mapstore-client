from django import template
from django.core.cache import caches

register = template.Library()


@register.simple_tag()
def get_services_dict():
    services_cache = caches["services_cache"]

    data = services_cache.get("search_options_services")
    if data and data is not None:
        return data

    return_val = populate_search_service_options()

    services_cache.set("search_options", return_val)

    return return_val

def populate_search_service_options():
    from geonode_mapstore_client.models import SearchService

    return_val = []
    
    for item in SearchService.objects.iterator():
        return_val.append(
            {
                "type": "wfs",
                "priority": item.priority,
                "displayName": f"{item.display_name}",
                "options": {
                    "url": f"{item.url}",
                    "typeName": f"{item.typename}",
                    "queriableAttributes": item.attributes,
                    "sortBy": f"{item.sortby}",
                    "srsName": f"{item.srsName}",
                    "maxFeatures": f"{item.maxFeatures}",
                }
            }
        )
    return return_val