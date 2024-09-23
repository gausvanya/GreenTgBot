from tortoise import Model, fields


class Report(Model):
    chat_id = fields.IntField()
    user_id = fields.IntField()
    admin_id = fields.IntField()
    reason = fields.CharField(256)
    chat_message_id = fields.IntField()
    admin_chat_id = fields.IntField()
    admin_message_id = fields.IntField()

    class Meta:
        table = 'chat_reports'