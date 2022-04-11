from utility.data_optimized import User
import requests
import json
import time


start_time = time.time()
u = User('1649689188061-693')

test = u.antiInteractions()

headers = {"content-type": "application/json"}
r = requests.post('http://localhost:8501/v1/models/DCN:predict', json.dumps({"signature_name": "serving_default", "instances": test.to_dict('records')}))
pred = json.loads(r.content.decode('utf-8'))
print(dict(zip(test['article_id'], sum(pred['predictions'], []))))

print(test)
end_time = time.time()

print("Took {} seconds to run".format(end_time-start_time))