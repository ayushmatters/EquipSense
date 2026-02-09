from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('otp_code', models.CharField(max_length=6)),
                ('purpose', models.CharField(choices=[('registration', 'Registration'), ('login', 'Login'), ('password_reset', 'Password Reset'), ('email_verification', 'Email Verification')], default='registration', max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('max_attempts', models.IntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('temp_username', models.CharField(blank=True, max_length=150, null=True)),
                ('temp_first_name', models.CharField(blank=True, max_length=150, null=True)),
                ('temp_last_name', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'verbose_name': 'OTP Record',
                'verbose_name_plural': 'OTP Records',
                'db_table': 'otp_records',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['email', 'is_verified'], name='otp_records_email_90692e_idx'), models.Index(fields=['created_at'], name='otp_records_created_d20c40_idx'), models.Index(fields=['expires_at'], name='otp_records_expires_b98a7e_idx')],
            },
        ),
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_or_email', models.CharField(max_length=255)),
                ('ip_address', models.GenericIPAddressField()),
                ('success', models.BooleanField(default=False)),
                ('failure_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Login Attempt',
                'verbose_name_plural': 'Login Attempts',
                'db_table': 'login_attempts',
                'ordering': ['-attempted_at'],
                'indexes': [models.Index(fields=['ip_address', 'attempted_at'], name='login_attem_ip_addr_bdf4e7_idx'), models.Index(fields=['username_or_email', 'attempted_at'], name='login_attem_usernam_03ab20_idx')],
            },
        ),
        migrations.CreateModel(
            name='GoogleAuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('token_type', models.CharField(max_length=50)),
                ('expires_at', models.DateTimeField()),
                ('scope', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='google_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Google Auth Token',
                'verbose_name_plural': 'Google Auth Tokens',
                'db_table': 'google_auth_tokens',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_email_verified', models.BooleanField(default=False)),
                ('is_admin_user', models.BooleanField(default=False)),
                ('google_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('profile_picture', models.URLField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('login_count', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'db_table': 'user_profiles',
                'indexes': [models.Index(fields=['google_id'], name='user_profil_google__6d4473_idx'), models.Index(fields=['is_email_verified'], name='user_profil_is_emai_f8e735_idx')],
            },
        ),
    ]
