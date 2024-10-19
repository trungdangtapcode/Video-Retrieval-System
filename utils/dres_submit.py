import requests

evaluationID = '69ec2262-d829-4ac1-94a2-1aa0a6693266'  # Replace with actual evaluation ID
sessionID = '2MUL165u1Zl0yjefkhOiNobfj8-YW6yV'        # Replace with actual session ID
def submit_kis(VIDEO_ID, TIME):
    url = f'https://eventretrieval.one/api/v2/submit/{evaluationID}'
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'session': sessionID
    }
    data = {
        "answerSets": [
            {
                "answers": [
                    {
                        "mediaItemName": VIDEO_ID,
                        "start": TIME,
                        "end": TIME
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, params=params, json=data)

    return response.json()

def submit_qa(ANSWER_QA):
    url = f'https://eventretrieval.one/api/v2/submit/{evaluationID}'
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'session': sessionID
    }
    data = {
        "answerSets": [
            {
                "answers": [
                    {
                        "text": ANSWER_QA
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, params=params, json=data)

    return response.json()