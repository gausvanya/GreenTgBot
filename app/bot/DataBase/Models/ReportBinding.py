from tortoise import Model, fields


class ReportBinding(Model):
    chat_id = fields.IntField()
    admin_chat_id = fields.IntField()

    class Meta:
        table = 'Report_binding'