from marshmallow import Schema, fields, ValidationError, validates_schema, validates


class SensorDataSchema(Schema):
    start_time = fields.DateTime(required=True, format='iso')
    end_time = fields.DateTime(required=True, format='iso')
    columns = fields.List(fields.String(), allow_none=True)

    PERMISSIBLE_COLUMNS_VALUE = {'date', 'p1', 'p2', 'pressure', 'humidity', 'temperature'}

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_time'] > data['end_time']:
            raise ValidationError("Start time later then end time")

    @validates('columns')
    def check_columns_value(self, values):
        for i in values:
            if i not in self.PERMISSIBLE_COLUMNS_VALUE:
                raise ValidationError(f"Unknown column value {i}")


class ForecastRequestSchema(Schema):
    start_time = fields.DateTime(allow_none=True, format='iso')
    end_time = fields.DateTime(allow_none=True, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if 'start_time' in data and 'end_time' in data and data['start_time'] > data['end_time']:
            raise ValidationError("Start date later then end date")


class AnomalyRequestSchema(Schema):
    start_time = fields.DateTime(required=True, format='iso')
    end_time = fields.DateTime(required=True, format='iso')

    @validates_schema
    def end_early_then_start(self, data, **kwargs):
        if data['start_time'] > data['end_time']:
            raise ValidationError("Start time later then end time")
