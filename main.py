from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

inprogress_order={}
app = FastAPI()

@app.route("/", methods=['POST', 'GET'])
async def handle_request(request: Request):
    if request.method == 'POST':
        # Retrieve the JSON data from the request
        payload = await request.json()

        # Extract the necessary information from the payload
        # based on the structure of the WebhookRequest from Dialogflow
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id=generic_helper.get_session_id(output_contexts[0]['name'])
        intent_handler_dict = {
            'track.order-context: ongoing-tracking': track_order,
            'order.add-context: ongoing-order': add_to_order,
            'order.complete-context : ongoing-order':complete_order,
            'order.remove-context:ongoing-order':remove_order

        }
        return intent_handler_dict[intent](parameters,session_id)
    elif request.method == 'GET':
        return JSONResponse(content={"message": "GET request received, but this endpoint only accepts POST requests."})


def save_to_database(order:dict):
    next_order_id=db_helper.get_next_order_id()
    for food_items,quantity in order.items():
        recode=db_helper.insert_order_items(food_items,quantity,next_order_id)
        
        if recode == -1:
            return-1
        
    db_helper.insert_order_tracking_items(next_order_id,'In progress')
    return next_order_id


    
def add_to_order(parameters: dict,session_id:str):
    food_items = parameters['food-items']
    quantities = parameters['number']

    if len(food_items) != len(quantities):
        fulfillment_text = 'Sorry! Can you please specify food items and quantities properly.'
    else:
        # print(len(food_items))
        # print(len(quantities))
        new_food_dict=dict(zip(food_items,quantities))
        
        if session_id in inprogress_order:
            current_food_dict=inprogress_order[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_order[session_id]=current_food_dict
        else:
            inprogress_order[session_id] = new_food_dict
        order_str=generic_helper.get_str_from_food_dict(inprogress_order[session_id])
        fulfillment_text = f'so far you have {order_str}. Do you want anything else?'

    return JSONResponse(content={'fulfillmentText': fulfillment_text})

def complete_order(parameters:dict,session_id:str):
    if session_id not in inprogress_order:
        fullfillemnt_text='Sorry I am having trouble to finding your order. Sorry can you place a new order?'
    else:
        order=inprogress_order[session_id]
        order_id=save_to_database(order)
        if order_id==-1:
            fulfillment_text='Sorry,I could not place your order,due to server problem.Can you please place a new order again? '
        else:
            total_price=db_helper.get_total_price(order_id)
            fulfillment_text=f'Your Order is done, here is your order id :{order_id}, You have to pay {total_price}$,when you get it.'
        del inprogress_order[session_id]
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
    

def remove_order(parameters:dict,session_id:str):
    if session_id  not in inprogress_order:
        fulfillment_text='Sorry I am having trouble to finding your order.'
    else:
        current_order=inprogress_order[session_id]
        food_items=parameters['food-items']
        removed_items=[]
        non_removed_items=[]
        for item in food_items:
            if item not in current_order:
                non_removed_items.append(item)
            else:
                removed_items.append(item)
                del current_order[item]
        if len(removed_items)>0:
            fulfillment_text = f"Remove {', '.join(removed_items)} from your order!"
        if len(non_removed_items) > 0:
            fulfillment_text = f'Your current order does not have {", ".join(non_removed_items)} items'

        if len(current_order.keys())==0:
            fulfillment_text='your order is empty'
        else:
            remaining_foods=generic_helper.get_str_from_food_dict(current_order)
            fulfillment_text=f'Your reamaining order is: {remaining_foods}'
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

    


def track_order(parameters: dict,session_id:str):
    order_id = int(parameters['number'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"
    return JSONResponse(content={"fulfillmentText": fulfillment_text})
