# baxting/tenant_loader.py
from django.template.loaders.base import Loader as BaseLoader
from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.template.loaders.app_directories import Loader as AppDirectoriesLoader
from django.db import connection
from django_tenants.utils import get_public_schema_name
from django.template import TemplateDoesNotExist


class TenantTemplateLoader(BaseLoader):
    """
    Custom template loader that first looks for tenant-specific templates
    before falling back to default templates.
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.loaders = [
            FilesystemLoader(engine),
            AppDirectoriesLoader(engine),
        ]

    def get_template_sources(self, template_name):
        tenant_schema = getattr(connection, "schema_name", get_public_schema_name())

        # Tenant-specific template path
        tenant_template_path = f"{tenant_schema}/{template_name}"
        for loader in self.loaders:
            yield from loader.get_template_sources(tenant_template_path)

        # Default template path
        for loader in self.loaders:
            yield from loader.get_template_sources(template_name)

    def get_contents(self, origin):
        for loader in self.loaders:
            try:
                return loader.get_contents(origin)
            except Exception:
                continue
        raise TemplateDoesNotExist(origin)

    def get_template(self, template_name, skip=None):
        tenant_schema = getattr(connection, "schema_name", get_public_schema_name())
        tenant_template_name = f"{tenant_schema}/{template_name}"
        # print(f"Looking for template: {tenant_template_name}")

        # Try tenant-specific template first
        for loader in self.loaders:
            try:
                return loader.get_template(tenant_template_name, skip=skip)
            except TemplateDoesNotExist:
                continue
            except Exception:
                continue

        # Fallback to default template
        for loader in self.loaders:
            try:
                return loader.get_template(template_name, skip=skip)
            except TemplateDoesNotExist:
                continue
            except Exception:
                continue

        raise TemplateDoesNotExist(f"Template '{template_name}' not found for tenant '{tenant_schema}'.")
