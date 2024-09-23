from tortoise import Model, fields


class Rules(Model):
    chat_id = fields.IntField(primary_key=True)
    text = fields.CharField(max_length=4096)

    class Meta:
        table = 'chat_rules'