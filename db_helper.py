import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hritamdey@61",
    database="pandeyji_eatery"
)


def get_order_status(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = "SELECT status FROM order_tracking WHERE order_id = %s"  # Using placeholder %s for order_id
    cursor.execute(query, (order_id,))  # Passing order_id as a tuple

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None
def get_next_order_id():

    Cursor=cnx.cursor()

    query='SELECT MAX(order_id) FROM orders'

    Cursor.execute(query)

    result=Cursor.fetchone()[0]

    Cursor.close()

    if result is None:
        return 1
    else:
        return result+1
    
def insert_order_items(food_items, quantity, order_id):
    try:
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', (food_items, quantity, order_id))

        # Committing the changes
        cnx.commit()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err.msg}")  # Print specific error message
        # Rollback changes if necessary
        cnx.rollback()

        return -1

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()


def get_total_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    return result


# if __name__=='__main__':
#     print(get_total_price(40))

def insert_order_tracking_items(order_id, status):
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()
