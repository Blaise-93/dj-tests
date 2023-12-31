# Generated by Django 4.2 on 2023-11-12 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leads', '0025_alter_lead_agent'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisOfClinicalProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinical_problem', models.CharField(max_length=50)),
                ('assessment', models.CharField(max_length=50)),
                ('priority', models.CharField(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], max_length=50)),
                ('action_taken_or_future_plan', models.CharField(max_length=500, verbose_name='Action Taken/Future Plan')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Analysis of Clinical Problems',
            },
        ),
        migrations.CreateModel(
            name='FollowUpPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follow_up_requirement', models.CharField(max_length=100)),
                ('action_taken_and_future_plan', models.CharField(max_length=100, verbose_name='Action Taken/Future Plan')),
                ('state_of_improvement_by_score', models.CharField(default='70%', max_length=4)),
                ('has_improved_than_before', models.BooleanField(default=False)),
                ('adhered_to_medications_given', models.BooleanField(default=False)),
                ('referral', models.CharField(max_length=50)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicationChanges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication_list', models.CharField(max_length=50)),
                ('dose', models.CharField(max_length=30)),
                ('frequency', models.CharField(default='BD', max_length=30)),
                ('route', models.CharField(default='Oral', max_length=20)),
                ('indication', models.CharField(blank=True, max_length=200, null=True)),
                ('start_or_continued_date', models.CharField(max_length=50, verbose_name='Start/Continued Date')),
                ('stop_date', models.CharField(max_length=50)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Medication Changes',
            },
        ),
        migrations.CreateModel(
            name='MedicationHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication_list', models.CharField(max_length=600)),
                ('indication_and_evidence', models.CharField(max_length=600)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Medication History',
            },
        ),
        migrations.CreateModel(
            name='MonitoringPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_used', models.CharField(max_length=100)),
                ('justification', models.CharField(max_length=300)),
                ('frequency', models.CharField(default='On admission and then 6 hours after', max_length=100, verbose_name='Result(s) and Action Plan')),
                ('results_and_action_plan', models.CharField(max_length=300)),
                ('has_improved', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_charge', models.PositiveBigIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('leads', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.lead')),
                ('medical_history', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.medicationhistory')),
            ],
        ),
        migrations.CreateModel(
            name='ProgressNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(verbose_name="patient's note")),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PharmaceuticalCarePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_unique_code', models.CharField(max_length=20)),
                ('analysis_of_clinical_problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.analysisofclinicalproblem')),
                ('follow_up_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.followupplan')),
                ('medication_changes', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.medicationchanges')),
                ('monitoring_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.monitoringplan')),
                ('patients', models.ManyToManyField(to='pharmcare.patient')),
                ('progress_note', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmcare.progressnote')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatientDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('marital_status', models.CharField(choices=[('Married', 'Married'), ('Single', 'Single'), ('Married with Kids', 'Married with Kids'), ('Married without Kids', 'Married without Kids'), ('Divorced', 'Divorced'), ('Single Parent', 'Single Parent'), ('Other', 'Other')], default='Single', max_length=20)),
                ('patient_class', models.CharField(choices=[('Adult', 'Adult'), ('Child', 'Child'), ('Toddler', 'Toddler'), ('Adolescent', 'Adolescent'), ('Elderly', 'Elderly')], default='Adult', max_length=20)),
                ('age', models.PositiveIntegerField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('height', models.CharField(max_length=20)),
                ('BMI', models.CharField(max_length=10)),
                ('patient_history', models.TextField()),
                ('past_medical_history', models.CharField(blank=True, max_length=500, null=True)),
                ('social_history', models.CharField(max_length=250)),
                ('slug', models.SlugField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.agent', verbose_name='Pharmacist')),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='patient_details',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pharmcare.patientdetail'),
        ),
        migrations.AddField(
            model_name='patient',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
