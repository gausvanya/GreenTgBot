from tortoise import Model, fields


class Agents(Model):
    user_id = fields.IntField(True)
    admin_id = fields.IntField()
    st_agent = fields.BooleanField(null=True)
    gl_agent = fields.BooleanField(null=True)
    date = fields.CharField(null=True, max_length=50)

    class Meta:
        table = 'agents'