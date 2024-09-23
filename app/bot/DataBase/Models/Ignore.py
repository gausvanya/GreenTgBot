from tortoise import Model, fields


class Ignore(Model):
    id = fields.IntField(primary_key=True)
    user_id = fields.IntField()
    admin_id = fields.IntField()
    reason = fields.CharField(max_length=4096)
    activity = fields.BooleanField()

    class Meta:
        table = 'ignore'