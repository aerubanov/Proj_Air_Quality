from marshmallow import Schema, fields, ValidationError, validates, validates_schema
from datetime import datetime


class SensorDataSchema(Schema):
    start_time = fields.DateTime(required=True, format='rfc')
    end_time = fields.DateTime(required=True, format='rfc')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_time'] > data['end_time']:
            raise ValidationError("Start time later then end time")
