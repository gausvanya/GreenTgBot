from tortoise import Model, fields


class Admins(Model):
    chat_id = fields.IntField()
    user_id = fields.IntField()
    rang = fields.IntField()

    class Meta:
        table = 'chat_admins'