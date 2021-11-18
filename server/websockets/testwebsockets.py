import aiohttp
import asyncio
import boto3
import os
import json

counter = 0
max_amount = 20
URL = "https://1n1v00okbh.execute-api.eu-central-1.amazonaws.com/prod"

async def listen():
    global counter
    global max_amount
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(URL) as ws:
            counter += 1
            print(f"Connected: {counter}/{max_amount}")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if 'Hello' in msg.data:
                        time.sleep(0.02)
                        await ws.close()
                        max_amount -= 1
                        print(f"{msg.data} - Disconected: {max_amount} still left.")
                        break
                    else:
                        await ws.send_str(msg.data + '/answer')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break


async def main():
    tasks = []
    for i in range(max_amount):
        task = asyncio.create_task(listen())
        await asyncio.sleep(0.05)
        tasks.append(task)

    for task in tasks:
        await task
    

async def disconnect(connections):
    global max_amount
    global URL
    if connections == max_amount:
        dynamo = boto3.client('dynamodb', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                              aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                              region_name='eu-central-1')

        client = boto3.client("apigatewaymanagementapi", endpoint_url=URL,
                              aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                              aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                              region_name='eu-central-1')

        connectionIds = dynamo.scan(TableName="websocket_ids")
        for connection in connectionIds["Items"]:
            msg = {"message": "Hello " + str(connection["connectionId"]["S"])}
            response = client.post_to_connection(ConnectionId=connection["connectionId"]["S"], Data=json.dumps(msg))
            print(response)
        return "message sent !"




if __name__ == "__main__":
    print("Websocket testing started.")

    import time
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")