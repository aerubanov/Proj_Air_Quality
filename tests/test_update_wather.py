import datetime

from scripts.update_wather import check_file, get_link
import re


def test_check_file(tmpdir):
    dir_name = 'test_data'
    d = tmpdir.mkdir(dir_name)

    res = check_file('some_file.csv', data_folder=dir_name)
    assert res == (False, None)

    f1 = d.join("empty.csv")
    f1.write('')
    res = check_file(f1, data_folder=dir_name)
    assert res == (False, None)

    f2 = d.join("data.csv")
    f2.write(""""Местное время в Москве (центр, Балчуг)";"T";"Po";"P";"Pa";"U";"DD";"Ff";"ff10";"ff3";"N";"WW";"""
             """"W1";"W2";"Tn";"Tx";"Cl";"Nh";"H";"Cm";"Ch";"VV";"Td";"RRR";"tR";"E";"Tg";"E'";"sss"\n"""
             """"08.12.2019 21:00";"2.7";"743.4";"754.9";"";"83";"Ветер, дующий с запада";"1";"";"";"90  или более,"""
             """ но не 100%";" ";"";"";"";"3.6";"Слоисто-кучевых, слоистых, кучевых или кучево-дождевых облаков";"""
             """ нет. "90  или более, но не 100%";"2500 или более, или облаков нет.";"Высококучевые просвечивающие,"""
             """ полосами, либо один или несколько слоев высококучевых просвечивающих, распространяющихся по небу;"""
             """ эти высококучевые в целом уплотняются.";"Перистых, перисто-кучевых или перисто-слоистых нет.";"""
             """  "10.0";"0.0";"Осадков нет";"12";"";"";"";""\n""")
    res = check_file(f2, data_folder=dir_name)
    assert res == (True, datetime.datetime(2019, 12, 9).date())


def test_get_link():
    end_date = datetime.date.today()-datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=7)
    link = get_link(start_date, end_date)
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    assert re.match(regex, link) is not None
