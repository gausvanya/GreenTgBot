from tortoise import Model, fields


class Bans(Model):
    chat_id = fields.IntField()
    user_id = fields.IntField()
    admin_id = fields.IntField()
    reason = fields.CharField(max_length=256)
    timestamp = fields.IntField(null=True)
    time_int = fields.IntField(null=True)
    time_type = fields.CharField(max_length=20)
    current_timestamp = fields.IntField()
    admin_rang = fields.IntField()

    class Meta:
        table = 'chat_bans'