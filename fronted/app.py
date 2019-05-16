from flask import Flask
from db.MongoDB import MongoDBClient
from config.config import get_config
from jinja2 import Environment,PackageLoader
from flask import render_template
from MachineLearning.random_forest import Predict
from MachineLearning.training_set_deal import gen_X
import time
import datetime
app = Flask(__name__)
env = Environment(loader=PackageLoader('fronted','templates'))

mongodb_settings = {
    'MONGODB_URL':get_config('db','MONGODB_URL'),
    'MONGODB_DB': get_config('db','MONGODB_DB'),
    'MONGODB_BATCH_SIZE': int(get_config('db','MONGODB_BATCH_SIZE')),
}

mongodb = MongoDBClient(mongodb_settings)

@app.route('/')
def hello_world():
    data = {}
    data['usdts'] = mongodb.find_sort_limit(collection='gate_data',query={'param':'tradeHistory-btm_usdt'},
                                    sort={'time':-1},limit=15,get_data=True)
    data['btcs'] = mongodb.find_sort_limit(collection='gate_data',query={'param':'tradeHistory-btm_btc'},
                                    sort={'time':-1},limit=30,get_data=True)
    data['eths'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'tradeHistory-btm_eth'},
                            sort={'time': -1}, limit=30,get_data=True)
    data['mk_usdt'] = mongodb.find_sort_limit(collection='gate_data',query={'param':'marketlist-btm_usdt'},
                                              sort={'time':-1},limit=1,get_data=True)
    data['mk_btc'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'marketlist-btm_btc'},
                                              sort={'time': -1}, limit=1, get_data=True)
    data['mk_eth'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'marketlist-btm_eth'},
                                              sort={'time': -1}, limit=1, get_data=True)
    data['tc_usdt'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'ticker-btm_usdt'},
                                              sort={'time': -1}, limit=1, get_data=True)
    data['tc_btc'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'ticker-btm_btc'},
                                             sort={'time': -1}, limit=1, get_data=True)
    data['tc_eth'] = mongodb.find_sort_limit(collection='gate_data', query={'param': 'ticker-btm_eth'},
                                             sort={'time': -1}, limit=1, get_data=True)
    if data['mk_usdt']:
        data['mk_usdt'] = data['mk_usdt'][0]
    if data['mk_btc']:
        data['mk_btc'] = data['mk_btc'][0]
    if data['mk_eth']:
        data['mk_eth'] = data['mk_eth'][0]
    if data['tc_usdt']:
        data['tc_usdt'] = data['tc_usdt'][0]
    if data['tc_btc']:
        data['tc_btc'] = data['tc_btc'][0]
    if data['tc_eth']:
        data['tc_eth'] = data['tc_eth'][0]

    gte = int(time.mktime(time.strptime(datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")))
    lte = int(time.mktime(time.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")))

    amount_sum = mongodb.find(collection='blockmeta_data',query={'timestamp':{'$gte':gte,'$lte':lte}})
    vector = gen_X(amount_sum)
    data['amount_sum'] = vector[0]
    data['count'] = vector[1]
    data['predict'] = Predict([vector])[0]

    return render_template('blockchain2.html',**data)
if __name__=="__main__":
    app.run()