from queue import Queue


def test_queue():
    q = Queue(10)
    for i in range(0, 12):
        q.add_item(i)
    assert len(q) == 10
