from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):

    creation_date = models.DateTimeField(verbose_name=_('Fecha Creacion'),
                                         auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name=_('Ultima Actualizacion'),
                                        auto_now=True
                                        )
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

