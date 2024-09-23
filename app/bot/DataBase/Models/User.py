from tortoise import Model, fields


class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=32)
    full_name = fields.CharField(max_length=128)

    class Meta:
        table = 'users'
