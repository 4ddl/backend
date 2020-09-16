# Generated by Django 3.1.1 on 2020-09-16 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problem', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('verdict', models.CharField(choices=[('P', 'Pending'), ('R', 'Running'), ('AC', 'Accepted'), ('PE', 'Presentation Error'), ('TLE', 'Time Limit Exceeded'), ('MLE', 'Memory Limit Exceeded'), ('WA', 'Wrong Answer'), ('RE', 'Runtime Error'), ('OLE', 'Output Limit Exceeded'), ('CE', 'Compile Error'), ('SE', 'System Error'), ('SYNC', 'Syncing Data')], default='P', max_length=10)),
                ('lang', models.CharField(max_length=10)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_rejudge_time', models.DateTimeField(default=None, null=True)),
                ('time_spend', models.IntegerField(null=True)),
                ('memory_spend', models.IntegerField(null=True)),
                ('time_cost', models.IntegerField(null=True)),
                ('memory_cost', models.IntegerField(null=True)),
                ('additional_info', models.JSONField(default=None, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='problem.problem')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
