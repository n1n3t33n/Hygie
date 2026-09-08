from django.contrib import admin

from apps.missions.models import Mission, Realise, Tournee


class RealiseInline(admin.TabularInline):
    model = Realise
    extra = 1


@admin.register(Tournee)
class TourneeAdmin(admin.ModelAdmin):
    list_display = ('id_tournee', 'date_tournee', 'createur')
    list_filter = ('date_tournee',)
    search_fields = ('createur__utilisateur__username',)
    date_hierarchy = 'date_tournee'


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('id_mission', 'reservation', 'tournee', 'demarree_le', 'terminee_le')
    list_filter = ('tournee',)
    search_fields = ('reservation__client__utilisateur__username',)
    inlines = [RealiseInline]
    exclude = ('agents',)  # géré via RealiseInline — Django impose ça dès qu'un `through` est défini