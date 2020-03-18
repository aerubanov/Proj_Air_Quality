from marshmallow import Schema, fields, ValidationError, validates_schema


class SensorDataSchema(Schema):
    start_time = fields.DateTime(required=True, format='iso')
    end_time = fields.DateTime(required=True, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_time'] > data['end_time']:
            raise ValidationError("Start time later then end time")


class ForecastRequestSchema(Schema):
    start_time = fields.DateTime(allow_none=True, format='iso')
    end_time = fields.DateTime(allow_none=True, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if 'start_time' in data and 'end_time' in data and data['start_time'] > data['end_time']:
            raise ValidationError("Start date later then end date")
