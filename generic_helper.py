import re

def get_session_id(session_str: str):
    exp='/sessions/(.*)/contexts'
    result=re.findall(exp,session_str)
    if result:
        extracted_str=result[0]
        return extracted_str
    return ""

def get_str_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(value)} {key}"for key,value in food_dict.items()])

if __name__=="__main__":
    print(get_str_from_food_dict({"samosa": 2,'chole':3}))

# if __name__=="__main__":
#     print(get_session_id( "projects/mira-chatbot-jeox/agent/sessions/4fb68bf7-2b32-38e3-a733-2a9184063574/contexts/ongoing-order"))

