import pandas as pd
"Complete thes functions or write your own to perform the following tasks"

def calculate_profit_by_order(orders_df):
    "Calculate profit for each order in the DataFrame"
    
    orders_df['Profit'] = ((orders_df['List Price'] - (orders_df['List Price'] * (orders_df['Discount Percent'] / 100)) #factor in discount price, 
                             - orders_df['cost price'])#profit = unit price - unit cost
                            * orders_df['Quantity']) #multiply by quantity

    return orders_df

def calculate_most_profitable_region(orders_df):
    "Calculate the most profitable region and its profit"

    profit_orders_df = calculate_profit_by_order(orders_df)
    #get df with profit column
    region_profit_df = profit_orders_df.groupby('Region')['Profit'].sum().nlargest(1).reset_index(name='Most Profitable Region')
    #nlargest returns most profitable region, transform into dataframe
    region_profit_df = region_profit_df.rename(columns={"Profit": "Total Profit"})
    return region_profit_df

def find_most_common_ship_method(orders_df):
    "Find the most common shipping method for each Category"
    
    category_mcsm = orders_df.groupby('Category')['Ship Mode'].agg(lambda x: x.mode()[0]).reset_index()
    #mcsm = most common shipping method
    #have to use [0] in case there are multiple most common methods per category
    #ideally i would want to set up an alert if this happens but seems outside of project scope
    category_mcsm = category_mcsm.rename(columns={"Ship Mode": "Most Common Shipping Method"})
    
    return category_mcsm

def find_number_of_order_per_category(orders_df):
    "find the number of orders for each Category and Sub Category"
    profit_df = calculate_profit_by_order(orders_df)
    cat_orders = profit_df.groupby("Category").size().reset_index(name='Amount Ordered')
    #get amt of orders per category
    cat_orders['Type'] = 'Category'
    #make column to distinguish between category and subcategory
    cat_orders = cat_orders.rename(columns={"Category": "Name"})
    #rename column to have same name as subcategory for concat 
    #repeat the same operation for subcategory
    subcat_orders = profit_df.groupby("Sub Category").size().reset_index(name='Amount Ordered')
    subcat_orders['Type'] = 'Sub Category'
    subcat_orders = subcat_orders.rename(columns={"Sub Category": "Name"})
    #combine together for final result
    final_df = pd.concat([cat_orders, subcat_orders], ignore_index=True)

    return final_df
