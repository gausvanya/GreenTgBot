from tortoise import Model, fields


class Notes(Model):
    chat_id = fields.IntField()
    name = fields.CharField(max_length=4096)
    text = fields.CharField(max_length=4096)
    number = fields.IntField()

    class Meta:
        table = 'chat_notes'