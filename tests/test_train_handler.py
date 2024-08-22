from cryptomanga.handler.train_handler import TrainHandler


def test_handler(train_handler: TrainHandler, create_event):
    #print(create_event["tweet_create_events"])
    value = train_handler.handle(create_event)
    print(value)