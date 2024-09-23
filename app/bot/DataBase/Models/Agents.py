from tortoise import Model, fields


class Agents(Model):
    user_id = fields.IntField(True)
    admin_id = fields.IntField()

    class Meta:
        table = 'agents'