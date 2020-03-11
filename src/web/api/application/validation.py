from marshmallow import Schema, fields, ValidationError, validates_schema


class SensorDataSchema(Schema):
    start_time = fields.DateTime(required=True, format='iso')
    end_time = fields.DateTime(required=True, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_time'] > data['end_time']:
            raise ValidationError("Start time later then end time")


class ForecastRequestSchema(Schema):
    start_date = fields.DateTime(required=False, format='iso')
    end_date = fields.DateTime(required=False, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_date'] is not None and data['end_date'] is not None and data['start_date'] > data['end_date']:
            raise ValidationError("Start date later then end date")
