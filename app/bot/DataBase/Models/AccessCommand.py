from tortoise import Model, fields


class AccessCommand(Model):
    chat_id = fields.IntField()
    command = fields.CharField(100)
    rang = fields.IntField()

    class Meta:
        table = 'access_command'