import boto3

# Table Model for mock table creation
def create_url_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://127.0.0.1:8000')

    table = dynamodb.create_table(
        TableName='Short_URL-to-Long_URL',
        KeySchema=[
            {
                'AttributeName': 'short_url',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'short_url',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName='Short_URL-to-Long_URL')
    assert table.table_status == 'ACTIVE'

    return table

if __name__ == '__main__':
    url_table = create_url_table()
    print("Table status:", url_table.table_status)