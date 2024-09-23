from tortoise import Model, fields


class Statistic(Model):
    user_id = fields.IntField()
    chat_id = fields.IntField()
    count = fields.IntField()
    date = fields.CharField(max_length=10)

    class Meta:
        table = 'chat_statistic'
