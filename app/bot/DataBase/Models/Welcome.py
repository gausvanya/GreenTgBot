from tortoise import Model, fields


class Welcome(Model):
    chat_id = fields.IntField(primary_key=True)
    photo_id = fields.CharField(max_length=150, null=True)
    text = fields.CharField(max_length=4096)

    class Meta:
        table = 'welcome_chat'
