from django.db import models


class User(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    referral = models.ForeignKey('self', related_name='referrals', on_delete=models.SET_NULL, null=True, blank=True)
    coins = models.IntegerField(default=0)

    def __str__(self):
        return self.username or str(self.telegram_id)


class CoinAccumulation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def stop_accumulation(self):
        self.is_active = False
        self.save()
