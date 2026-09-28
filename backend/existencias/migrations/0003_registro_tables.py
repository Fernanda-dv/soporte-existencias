from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('existencias', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='equipo',
            table='registro_equipos',
        ),
        migrations.AlterModelOptions(
            name='equipo',
            options={
                'verbose_name': 'Registro de equipo',
                'verbose_name_plural': 'Registros de equipos',
            },
        ),
        migrations.AlterModelTable(
            name='impresoraregistro',
            table='registro_impresoras',
        ),
        migrations.AlterModelOptions(
            name='impresoraregistro',
            options={
                'verbose_name': 'Registro de impresora',
                'verbose_name_plural': 'Registros de impresoras',
            },
        ),
    ]