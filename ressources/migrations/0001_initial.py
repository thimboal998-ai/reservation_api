import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ressource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True, verbose_name='nom')),
                ('type', models.CharField(choices=[('salle', 'Salle'), ('equipement', 'Equipement')], default='salle', max_length=20, verbose_name='type')),
                ('capacite', models.PositiveIntegerField(blank=True, help_text='Nombre de places. A renseigner pour les salles uniquement.', null=True, verbose_name='capacite')),
                ('active', models.BooleanField(default=True, help_text='Une ressource inactive ne peut plus etre reservee (regle 3).', verbose_name='active')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'ressource',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Indisponibilite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debut', models.DateTimeField(verbose_name='debut')),
                ('fin', models.DateTimeField(verbose_name='fin')),
                ('motif', models.CharField(max_length=255, verbose_name='motif')),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indisponibilites', to='ressources.ressource', verbose_name='ressource')),
            ],
            options={
                'verbose_name': 'indisponibilite',
                'verbose_name_plural': 'indisponibilites',
                'ordering': ['-debut'],
                'constraints': [models.CheckConstraint(condition=models.Q(('fin__gt', models.F('debut'))), name='indisponibilite_fin_apres_debut')],
            },
        ),
    ]
