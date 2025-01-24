from peewee import *
from datetime import datetime

DB = SqliteDatabase('PhantomTrackDB.sqlite')


class BaseModel(Model):
    class Meta:
        database = DB

class Role(BaseModel):
    id = AutoField(primary_key=True)
    role_name = CharField(max_length=10)


class Loyalty_level(BaseModel):
    id = AutoField(primary_key=True)
    loyalty_coeff = FloatField(default=0.05)
    sum = IntegerField()


class User(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    username = CharField()
    role = ForeignKeyField(Role, null=False, default=1, on_update='cascade')
    status = BooleanField(default=True)
    card_id = IntegerField(unique=True, default=0)
    loyalty_points = IntegerField(default=30)
    money_paid = IntegerField(default=0, constraints=[Check('money_paid >= 0')])
    loyalty_level = ForeignKeyField(Loyalty_level, null=False, default=3, on_update='cascade')


class ArtistModel(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()


class Statistics(BaseModel):
    artist_id = ForeignKeyField(ArtistModel, null=False, on_update='cascade')
    year = IntegerField(default=datetime.now().year)
    quarter = IntegerField(constraints=[Check('quarter >= 1'), Check('quarter <= 4')])
    state = IntegerField(constraints=[Check('state >= 0'), Check('state <= 2')], default=0)


DB.create_tables([Role, Loyalty_level, User,ArtistModel, Statistics])
