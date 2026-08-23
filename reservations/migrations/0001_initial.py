import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ressources', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debut', models.DateTimeField(verbose_name='debut')),
                ('fin', models.DateTimeField(verbose_name='fin')),
                ('motif', models.TextField(verbose_name='motif')),
                ('nombre_participants', models.PositiveIntegerField(default=1, verbose_name='nombre de participants')),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('validee', 'Validee'), ('refusee', 'Refusee'), ('annulee', 'Annulee'), ('terminee', 'Terminee')], db_index=True, default='en_attente', max_length=20, verbose_name='statut')),
                ('commentaire_gestionnaire', models.TextField(blank=True, help_text='Obligatoire en cas de refus (regle 9).', verbose_name='commentaire du gestionnaire')),
                ('decide_le', models.DateTimeField(blank=True, null=True, verbose_name='date de decision')),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
                ('modifie_le', models.DateTimeField(auto_now=True)),
                ('decideur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decisions_reservations', to=settings.AUTH_USER_MODEL, verbose_name='decideur')),
                ('demandeur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to=settings.AUTH_USER_MODEL, verbose_name='demandeur')),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='ressources.ressource', verbose_name='ressource')),
            ],
            options={
                'verbose_name': 'reservation',
                'ordering': ['-debut'],
                'indexes': [models.Index(fields=['ressource', 'statut', 'debut'], name='idx_reservation_conflit')],
                'constraints': [models.CheckConstraint(condition=models.Q(('fin__gt', models.F('debut'))), name='reservation_fin_apres_debut')],
            },
        ),
    ]
