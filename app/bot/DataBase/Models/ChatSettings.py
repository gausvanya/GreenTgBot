from tortoise import Model, fields


class ChatSettings(Model):
    chat_id = fields.IntField()
    default_time_ban = fields.CharField(100)
    default_time_mute = fields.CharField(100)
    default_time_warn = fields.CharField(100)
    default_limit_warn = fields.IntField()
    default_result_warn = fields.CharField(100)


    class Meta:
        table = 'chat_settings'
