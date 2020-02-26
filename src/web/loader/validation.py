from marshmallow import Schema, fields, ValidationError, validates
from datetime import datetime


class SensorSchema(Schema):
    p1 = fields.Float(required=True)
    p2 = fields.Float(required=True)
    temp = fields.Float(required=True)
    press = fields.Float(required=True)
    hum = fields.Float(required=True)

    @validates('p1')
    def validate_p1(self, value):
        if value < 0:
            raise ValidationError('Negative P1 value')

    @validates('p2')
    def validate_p2(self, value):
        if value < 0:
            raise ValidationError('Negative P2 value')

    @validates('temp')
    def validate_temp(self, value):
        if value > 50:
            raise ValidationError(f'Temperature very high {value}')
        if value < -50:
            raise ValidationError(f'Temperature very low: {value}')

    @validates('press')
    def validate_press(self, value):
        if value > 109000:
            raise ValidationError(f'Pressure very high: {value}')
        if value < 85000:
            raise ValidationError(f'Pressure very low: {value}')

    @validates('hum')
    def validate_hum(self, value):
        if value > 100:
            raise ValidationError('Humidity higher 100')
        if value < 0:
            raise ValidationError('Negative humidity')


class MyDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data, **kwargs)


class WeatherSchema(Schema):
    date = fields.List(MyDateTimeField, required=True)
    prec = fields.List(fields.String, required=True)
    temp = fields.List(fields.Float, required=True)
    pressure = fields.List(fields.Float, required=True)
    wind_speed = fields.List(fields.Float, required=True)
    wind_dir = fields.List(fields.String, required=True)
    humidity = fields.List(fields.Float, required=True)

    PERMISSIBLE_WIND_DIR = ['С', 'Ю', 'З', 'В', 'С-В', 'С-З', 'Ю-З', 'Ю-В']

    @validates('pressure')
    def validate_press(self, value):
        for v in value:
            if v > 830:
                raise ValidationError(f'Pressure very high: {value}')
            if v < 670:
                raise ValidationError(f'Pressure very low: {value}')

    @validates('temp')
    def validate_temp(self, value):
        for v in value:
            if v > 50:
                raise ValidationError(f'Temperature very high {value}')
            if v < -50:
                raise ValidationError(f'Temperature very low: {value}')

    @validates('humidity')
    def validate_hum(self, value):
        for v in value:
            if v > 100:
                raise ValidationError('Humidity higher 100')
            if v < 0:
                raise ValidationError('Negative humidity')

    @validates('wind_speed')
    def validate_wind_speed(self, value):
        for v in value:
            if v < 0:
                raise ValidationError('Negative wind_speed')
            if v > 50:
                raise ValidationError("Wind spig higher 50")

    @validates('wind_dir')
    def validate_wind_dir(self, value):
        for v in value:
            if v not in self.PERMISSIBLE_WIND_DIR:
                raise ValidationError(f'Unknown wind dir: {v}')
