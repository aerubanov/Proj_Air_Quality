from marshmallow import Schema, fields, ValidationError, validates


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
