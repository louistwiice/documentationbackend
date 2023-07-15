from django.utils.translation import ugettext_lazy as _


class Countries:
    SENEGAL = 'sn'
    MALI = 'ml'
    COTE_IVOIRE = 'ci'
    BURKINA = 'bf'

    CHOICES = (
        (SENEGAL, _("Senegal")),
        (MALI, _("Mali")),
        (BURKINA, _("Burkina Faso")),
        (COTE_IVOIRE, _("Cote d'Ivoire")),
    )
